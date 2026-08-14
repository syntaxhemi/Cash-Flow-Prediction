from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from math import isfinite

from domain.exceptions import InvalidSimulationError
from ml import (
    ForecastFeaturePreparationService,
    ForecastInferenceService,
    LoadedForecastArtifacts,
)


@dataclass(frozen=True, slots=True)
class CounterfactualContext:
    """Baseline feature values used as the source for simulation patches."""

    temporal_rows: list[dict[str, float]]
    static_values: dict[str, float]
    baseline_prediction: Decimal
    solvency_buffer: Decimal


@dataclass(frozen=True, slots=True)
class CounterfactualEvaluation:
    """Prediction and comparison values for one counterfactual patch."""

    predicted_net_cashflow: Decimal
    delta_from_baseline: Decimal
    meets_buffer: bool


class CounterfactualEvaluator:
    """Evaluate validated static-feature patches through the shared ML runtime."""

    def __init__(self) -> None:
        """Initialize the feature preparation and inference services."""
        self._preparation = ForecastFeaturePreparationService()
        self._inference = ForecastInferenceService()

    def evaluate(
        self,
        context: CounterfactualContext,
        input_patch: Mapping[str, Decimal],
        artifacts: LoadedForecastArtifacts,
    ) -> CounterfactualEvaluation:
        """Evaluate one static-feature counterfactual.

        Args:
            context: Baseline temporal and static feature values.
            input_patch: Static feature replacements for this scenario.
            artifacts: Loaded model artifacts used for inference.

        Returns:
            Prediction and comparison values for the patched inputs.

        Raises:
            InvalidSimulationError: If the patch contains unsupported or non-finite
                feature values.
        """
        unknown_features = set(input_patch) - set(artifacts.metadata.static_features)
        if unknown_features:
            names = ', '.join(sorted(unknown_features))
            raise InvalidSimulationError(f'Unsupported simulation features: {names}.')

        static_values = context.static_values.copy()
        for name, value in input_patch.items():
            numeric_value = float(value)

            if not isfinite(numeric_value):
                raise InvalidSimulationError(
                    f'Simulation feature "{name}" must be finite.'
                )

            static_values[name] = numeric_value

        features = self._preparation.prepare(
            context.temporal_rows, static_values, artifacts.metadata
        )
        prediction = self._inference.predict(features, artifacts)
        predicted = Decimal(str(prediction.predicted_net_cashflow))
        return CounterfactualEvaluation(
            predicted_net_cashflow=predicted,
            delta_from_baseline=predicted - context.baseline_prediction,
            meets_buffer=predicted >= context.solvency_buffer,
        )
