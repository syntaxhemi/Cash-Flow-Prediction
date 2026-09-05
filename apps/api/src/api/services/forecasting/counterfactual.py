from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from math import isfinite

from database.models import ForecastRunModel
from domain.exceptions import InvalidSimulationError
from ml import (
    ForecastArtifactMetadata,
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


def build_counterfactual_context(
    forecast: ForecastRunModel, metadata: ForecastArtifactMetadata
) -> CounterfactualContext:
    """Build baseline feature values from a loaded forecast run.

    Args:
        forecast: Forecast ORM model with input relationships eagerly loaded.
        metadata: Loaded artifact metadata defining feature dimensions.

    Returns:
        Baseline temporal and static feature values for counterfactual evaluation.

    Raises:
        InvalidSimulationError: If the forecast does not contain the required input
            periods or was produced by a different artifact version.
    """
    if (
        forecast.model_version != metadata.model_version
        or forecast.artifact_version != str(metadata.artifact_version)
    ):
        raise InvalidSimulationError(
            'The baseline forecast uses a different model artifact. Run a new '
            'baseline forecast before starting a simulation.'
        )
    periods = sorted(forecast.periods, key=lambda period: period.sequence_index)
    if len(periods) != metadata.sequence_length:
        raise InvalidSimulationError(
            'The baseline forecast does not contain the required input periods.'
        )
    temporal_rows = [
        {
            'total_invoice_amount': float(
                period.monthly_cashflow_aggregate.total_invoice_amount
            ),
            'payment_delay': float(
                period.monthly_cashflow_aggregate.total_payment_delay_days
            ),
            'monthly_repayment': float(
                period.monthly_cashflow_aggregate.monthly_repayment
            ),
            'total_inflows': float(period.monthly_cashflow_aggregate.total_inflows),
            'total_outflows': float(period.monthly_cashflow_aggregate.total_outflows),
        }
        for period in periods
    ]
    snapshot = forecast.static_snapshot
    static_values = {
        'capex': float(snapshot.capex or 0),
        'cogs': float(snapshot.cogs or 0),
        'current_assets': float(snapshot.current_assets or 0),
        'current_liabilities': float(snapshot.current_liabilities or 0),
        'fixed_assets': float(snapshot.fixed_assets or 0),
        'long_term_liabilities': float(snapshot.long_term_liabilities or 0),
        'credit_score': float(snapshot.credit_score or 0),
        'failure_score': float(snapshot.failure_score or 0),
        'debt_to_revenue_ratio': float(snapshot.debt_to_revenue_ratio or 0),
        'missed_payments_number': float(snapshot.missed_payments_number or 0),
    }
    return CounterfactualContext(
        temporal_rows=temporal_rows,
        static_values=static_values,
        baseline_prediction=forecast.predicted_net_cashflow,
        solvency_buffer=forecast.solvency_buffer,
    )


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
        temporal_patch: Mapping[int, Mapping[str, Decimal]] | None = None,
    ) -> CounterfactualEvaluation:
        """Evaluate one static or temporal counterfactual.

        Args:
            context: Baseline temporal and static feature values.
            input_patch: Static feature replacements for this scenario.
            artifacts: Loaded model artifacts used for inference.
            temporal_patch: Optional temporal feature replacements keyed by sequence
                index.

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

        temporal_rows = [row.copy() for row in context.temporal_rows]
        if temporal_patch is not None:
            for index, patch in temporal_patch.items():
                if index < 0 or index >= len(temporal_rows):
                    raise InvalidSimulationError(
                        f'Temporal simulation index "{index}" is out of range.'
                    )
                unknown_temporal = set(patch) - set(
                    artifacts.metadata.temporal_features
                )
                if unknown_temporal:
                    names = ', '.join(sorted(unknown_temporal))
                    raise InvalidSimulationError(
                        f'Unsupported temporal simulation features: {names}.'
                    )
                for name, value in patch.items():
                    numeric_value = float(value)
                    if not isfinite(numeric_value):
                        raise InvalidSimulationError(
                            f'Temporal feature "{name}" must be finite.'
                        )
                    temporal_rows[index][name] = numeric_value

        features = self._preparation.prepare(
            temporal_rows, static_values, artifacts.metadata
        )
        prediction = self._inference.predict(features, artifacts)
        predicted = Decimal(str(prediction.predicted_net_cashflow))
        return CounterfactualEvaluation(
            predicted_net_cashflow=predicted,
            delta_from_baseline=predicted - context.baseline_prediction,
            meets_buffer=predicted >= context.solvency_buffer,
        )
