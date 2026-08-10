"""Configuration loading for the training pipeline."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class DataConfig:
    account_receivable_path: Path
    businesses_path: Path
    credit_account_history_path: Path
    credit_card_history_path: Path
    credit_rating_path: Path
    loan_path: Path


@dataclass(slots=True)
class SplitConfig:
    test_quantile: float
    random_state: int


@dataclass(slots=True)
class ModelConfig:
    epochs: int
    batch_size: int
    learning_rate: float
    lstm_hidden: int
    dense_hidden: int
    dropout: float
    early_stopping_patience: int


@dataclass(slots=True)
class FeatureConfig:
    sequence_length: int
    temporal_features: list[str]
    static_features: list[str]
    label_column: str


@dataclass(slots=True)
class ArtifactConfig:
    output_dir: Path
    run_name: str


@dataclass(slots=True)
class TrainingConfig:
    data: DataConfig
    split: SplitConfig
    model: ModelConfig
    features: FeatureConfig
    artifacts: ArtifactConfig


def load_config(config_path: Path) -> TrainingConfig:
    raw_config = yaml.safe_load(config_path.read_text(encoding='utf-8'))

    return TrainingConfig(
        data=DataConfig(
            account_receivable_path=Path(raw_config['data']['account_receivable_path']),
            businesses_path=Path(raw_config['data']['businesses_path']),
            credit_account_history_path=Path(
                raw_config['data']['credit_account_history_path']
            ),
            credit_card_history_path=Path(
                raw_config['data']['credit_card_history_path']
            ),
            credit_rating_path=Path(raw_config['data']['credit_rating_path']),
            loan_path=Path(raw_config['data']['loan_path']),
        ),
        split=SplitConfig(
            test_quantile=raw_config['split']['test_quantile'],
            random_state=raw_config['split']['random_state'],
        ),
        model=ModelConfig(**raw_config['model']),
        features=FeatureConfig(**raw_config['features']),
        artifacts=ArtifactConfig(
            output_dir=Path(raw_config['artifacts']['output_dir']),
            run_name=raw_config['artifacts']['run_name'],
        ),
    )


def config_to_dict(config: TrainingConfig) -> dict[str, Any]:
    return {
        'data': {key: str(value) for key, value in asdict(config.data).items()},
        'split': asdict(config.split),
        'model': asdict(config.model),
        'features': asdict(config.features),
        'artifacts': {
            'output_dir': str(config.artifacts.output_dir),
            'run_name': config.artifacts.run_name,
        },
    }
