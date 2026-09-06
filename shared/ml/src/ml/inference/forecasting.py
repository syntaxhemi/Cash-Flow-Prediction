from dataclasses import dataclass

import numpy as np
import torch

from ml.artifacts import LoadedForecastArtifacts
from ml.preparation.currency import ForecastCurrencyConverter
from ml.preparation.feature_preparation import PreparedForecastFeatures


@dataclass(frozen=True, slots=True)
class ForecastPrediction:
    """Prediction result with artifact provenance."""

    predicted_net_cashflow: float
    model_version: str
    artifact_version: int


class ForecastInferenceService:
    """Apply persisted scalers and run the loaded forecasting model."""

    def __init__(self) -> None:
        """Initialize inference-time currency normalization."""
        self._currency_converter = ForecastCurrencyConverter()

    def predict(
        self,
        features: PreparedForecastFeatures,
        artifacts: LoadedForecastArtifacts,
        input_currency: str | None = None,
    ) -> ForecastPrediction:
        """Predict next-period net cash flow for prepared features.

        Args:
            features: Validated unscaled temporal and static arrays.
            artifacts: Loaded model, scalers, and metadata.
            input_currency: Currency of monetary input values and requested output.

        Returns:
            Prediction and model artifact provenance.
        """
        currency = input_currency or artifacts.metadata.training_currency
        model_features = self._currency_converter.to_training_currency(
            features, artifacts.metadata, currency
        )
        temporal_scaled = artifacts.temporal_scaler.transform(model_features.temporal)
        static_scaled = artifacts.static_scaler.transform(model_features.static)
        temporal_tensor = torch.tensor(
            temporal_scaled[np.newaxis, :, :], dtype=torch.float32
        )
        static_tensor = torch.tensor(static_scaled, dtype=torch.float32)

        with torch.no_grad():
            prediction = artifacts.model(temporal_tensor, static_tensor)

        prediction_value = float(prediction.squeeze().item())
        if artifacts.target_scaler is not None:
            prediction_value = float(
                artifacts.target_scaler.inverse_transform(
                    np.asarray([[prediction_value]])
                )[0, 0]
            )
        model_weight = artifacts.metadata.persistence_model_weight
        maximum_zscore = float(
            max(np.max(np.abs(temporal_scaled)), np.max(np.abs(static_scaled)))
        )
        if maximum_zscore > artifacts.metadata.model_zscore_limit:
            model_weight = 0.0
        if model_weight < 1.0:
            inflow_index = artifacts.metadata.temporal_features.index('total_inflows')
            outflow_index = artifacts.metadata.temporal_features.index('total_outflows')
            cashflows = (
                model_features.temporal[:, inflow_index]
                - model_features.temporal[:, outflow_index]
            )
            persistence_prediction = float(np.mean(cashflows))
            prediction_value = (
                model_weight * prediction_value
                + (1.0 - model_weight) * persistence_prediction
            )
        prediction_value = self._currency_converter.prediction_to_input_currency(
            prediction_value, artifacts.metadata, currency
        )

        return ForecastPrediction(
            predicted_net_cashflow=prediction_value,
            model_version=artifacts.metadata.model_version,
            artifact_version=artifacts.metadata.artifact_version,
        )
