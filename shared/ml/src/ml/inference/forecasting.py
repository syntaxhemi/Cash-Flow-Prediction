from dataclasses import dataclass

import numpy as np
import torch

from ml.artifacts import LoadedForecastArtifacts
from ml.preparation import PreparedForecastFeatures


@dataclass(frozen=True, slots=True)
class ForecastPrediction:
    """Prediction result with artifact provenance."""

    predicted_net_cashflow: float
    model_version: str
    artifact_version: int


class ForecastInferenceService:
    """Apply persisted scalers and run the loaded forecasting model."""

    def predict(
        self,
        features: PreparedForecastFeatures,
        artifacts: LoadedForecastArtifacts,
    ) -> ForecastPrediction:
        """Predict next-period net cash flow for prepared features.

        Args:
            features: Validated unscaled temporal and static arrays.
            artifacts: Loaded model, scalers, and metadata.

        Returns:
            Prediction and model artifact provenance.
        """
        temporal_scaled = artifacts.temporal_scaler.transform(features.temporal)
        static_scaled = artifacts.static_scaler.transform(features.static)
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

        return ForecastPrediction(
            predicted_net_cashflow=prediction_value,
            model_version=artifacts.metadata.model_version,
            artifact_version=artifacts.metadata.artifact_version,
        )
