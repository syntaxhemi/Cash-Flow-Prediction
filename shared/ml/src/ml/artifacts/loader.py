import json
import pickle
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import torch
import yaml

from ml.models import RuntimeForecastModel, RuntimeModelConfig

EXPECTED_TEMPORAL_FEATURES = [
    'total_invoice_amount',
    'payment_delay',
    'monthly_repayment',
    'total_inflows',
    'total_outflows',
]
EXPECTED_STATIC_FEATURES = [
    'capex',
    'cogs',
    'current_assets',
    'current_liabilities',
    'fixed_assets',
    'long_term_liabilities',
    'credit_score',
    'failure_score',
    'debt_to_revenue_ratio',
    'missed_payments_number',
]


@dataclass(frozen=True, slots=True)
class ForecastArtifactMetadata:
    """Metadata describing one trained forecasting artifact bundle."""

    model_version: str
    artifact_version: int
    training_run_name: str
    created_at: datetime
    sequence_length: int
    temporal_features: list[str]
    static_features: list[str]
    label_column: str
    sequence_input_size: int
    static_input_size: int
    persistence_model_weight: float
    persistence_strategy: str
    model_zscore_limit: float
    artifact_files: dict[str, str]


@dataclass(slots=True)
class LoadedForecastArtifacts:
    """Runtime artifacts required for scaled forecasting inference."""

    run_directory: Path
    metadata: ForecastArtifactMetadata
    model: RuntimeForecastModel
    temporal_scaler: Any
    static_scaler: Any
    target_scaler: Any | None


class ModelArtifactLoader:
    """Load and cache one validated forecasting artifact bundle."""

    def __init__(self, run_directory: Path) -> None:
        """Initialize the artifact loader.

        Args:
            run_directory: Directory containing one training run's artifacts.
        """
        self._run_directory = run_directory
        self._loaded_artifacts: LoadedForecastArtifacts | None = None

    def load(self) -> LoadedForecastArtifacts:
        """Load, validate, and cache the configured artifact bundle.

        Returns:
            Loaded model, scalers, and metadata.

        Raises:
            ValueError: If metadata, architecture, or scaler dimensions are invalid.
            FileNotFoundError: If a required artifact file is missing.
        """
        if self._loaded_artifacts is not None:
            return self._loaded_artifacts

        metadata = self._load_metadata(self._run_directory / 'artifact_metadata.json')
        config = self._load_runtime_config(
            self._run_directory / metadata.artifact_files['config_snapshot']
        )
        self._validate_metadata(metadata)
        model = RuntimeForecastModel(
            metadata.sequence_input_size,
            metadata.static_input_size,
            config,
        )
        state_path = self._required_path(metadata, 'model')
        model.load_state_dict(
            torch.load(state_path, map_location='cpu', weights_only=True)
        )
        model.eval()

        temporal_scaler = self._load_pickle(
            self._required_path(metadata, 'temporal_scaler')
        )
        static_scaler = self._load_pickle(
            self._required_path(metadata, 'static_scaler')
        )
        target_scaler = None
        if 'target_scaler' in metadata.artifact_files:
            target_scaler = self._load_pickle(
                self._required_path(metadata, 'target_scaler')
            )
        self._validate_scaler(temporal_scaler, metadata.sequence_input_size, 'temporal')
        self._validate_scaler(static_scaler, metadata.static_input_size, 'static')
        if target_scaler is not None:
            self._validate_scaler(target_scaler, 1, 'target')

        self._loaded_artifacts = LoadedForecastArtifacts(
            run_directory=self._run_directory,
            metadata=metadata,
            model=model,
            temporal_scaler=temporal_scaler,
            static_scaler=static_scaler,
            target_scaler=target_scaler,
        )
        return self._loaded_artifacts

    def _required_path(self, metadata: ForecastArtifactMetadata, key: str) -> Path:
        """Resolve a required artifact path inside the configured run directory."""
        try:
            relative_path = metadata.artifact_files[key]
        except KeyError as error:
            raise ValueError(f'Artifact metadata does not define "{key}".') from error

        path = (self._run_directory / relative_path).resolve()

        try:
            path.relative_to(self._run_directory.resolve())
        except ValueError as error:
            raise ValueError(
                f'Artifact path for "{key}" escapes the run directory.'
            ) from error

        if not path.is_file():
            raise FileNotFoundError(f'Required artifact does not exist: {path}')
        return path

    @staticmethod
    def _load_pickle(path: Path) -> Any:
        """Load one pickled scaler artifact.

        Args:
            path: Pickle file path.

        Returns:
            Deserialized scaler.
        """
        with path.open('rb') as file_handle:
            return pickle.load(file_handle)

    @staticmethod
    def _load_metadata(path: Path) -> ForecastArtifactMetadata:
        """Load artifact metadata from JSON.

        Args:
            path: Metadata JSON path.

        Returns:
            Parsed artifact metadata.
        """
        raw = json.loads(path.read_text(encoding='utf-8'))
        return ForecastArtifactMetadata(
            model_version=str(raw['model_version']),
            artifact_version=int(raw['artifact_version']),
            training_run_name=str(raw['training_run_name']),
            created_at=datetime.fromisoformat(raw['created_at']),
            sequence_length=int(raw['sequence_length']),
            temporal_features=list(raw['temporal_features']),
            static_features=list(raw['static_features']),
            label_column=str(raw['label_column']),
            sequence_input_size=int(raw['sequence_input_size']),
            static_input_size=int(raw['static_input_size']),
            persistence_model_weight=float(raw.get('persistence_model_weight', 1.0)),
            persistence_strategy=str(raw.get('persistence_strategy', 'none')),
            model_zscore_limit=float(raw.get('model_zscore_limit', float('inf'))),
            artifact_files=dict(raw['artifact_files']),
        )

    @staticmethod
    def _load_runtime_config(path: Path) -> RuntimeModelConfig:
        """Load architecture parameters from the training config snapshot."""
        raw = yaml.safe_load(path.read_text(encoding='utf-8'))
        model = raw['model']
        return RuntimeModelConfig(
            lstm_hidden=int(model['lstm_hidden']),
            dense_hidden=int(model['dense_hidden']),
            dropout=float(model['dropout']),
        )

    @staticmethod
    def _validate_metadata(metadata: ForecastArtifactMetadata) -> None:
        """Validate metadata dimensions and feature declarations."""
        if metadata.sequence_length <= 0:
            raise ValueError('Artifact sequence_length must be positive.')
        if metadata.sequence_input_size != len(metadata.temporal_features):
            raise ValueError(
                'Temporal feature count does not match metadata dimensions.'
            )
        if metadata.static_input_size != len(metadata.static_features):
            raise ValueError('Static feature count does not match metadata dimensions.')
        if metadata.temporal_features != EXPECTED_TEMPORAL_FEATURES:
            raise ValueError(
                'Artifact temporal feature order does not match the runtime contract.'
            )
        if metadata.static_features != EXPECTED_STATIC_FEATURES:
            raise ValueError(
                'Artifact static feature order does not match the runtime contract.'
            )
        if metadata.label_column != 'net_cash_flow':
            raise ValueError('Artifact label_column must be "net_cash_flow".')
        if not 0.0 <= metadata.persistence_model_weight <= 1.0:
            raise ValueError(
                'Artifact persistence_model_weight must be between 0 and 1.'
            )
        expected_strategy = (
            'none' if metadata.persistence_model_weight == 1.0 else 'sequence_mean'
        )
        if metadata.persistence_strategy != expected_strategy:
            raise ValueError(
                'Artifact persistence_strategy does not match its model weight.'
            )
        if metadata.model_zscore_limit <= 0:
            raise ValueError('Artifact model_zscore_limit must be positive.')

    @staticmethod
    def _validate_scaler(scaler: Any, expected_features: int, name: str) -> None:
        """Validate a scaler's recorded feature dimension."""
        actual_features = getattr(scaler, 'n_features_in_', None)
        if actual_features != expected_features:
            raise ValueError(
                f'{name.capitalize()} scaler expects {actual_features} features; '
                f'expected {expected_features}.'
            )
