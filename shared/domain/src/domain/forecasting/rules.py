from datetime import date
from typing import Protocol

from domain.exceptions import InvalidForecastRunError


class IForecastingRules(Protocol):
    def validate_run(
        self,
        *,
        target_period_start: date,
        target_period_end: date,
        sequence_window_months: int,
        model_version: str,
        artifact_version: str,
    ) -> None:
        """Validate forecast target range and model metadata."""
        ...


class DefaultForecastingRules:
    def validate_run(
        self,
        *,
        target_period_start: date,
        target_period_end: date,
        sequence_window_months: int,
        model_version: str,
        artifact_version: str,
    ) -> None:
        """Validate forecast target range and model metadata.

        Args:
            target_period_start: First forecast target period.
            target_period_end: Last forecast target period.
            sequence_window_months: Number of historical months used.
            model_version: Loaded model version identifier.
            artifact_version: Loaded artifact version identifier.

        Raises:
            InvalidForecastRunError: If the forecast configuration is invalid.
        """
        if target_period_end < target_period_start:
            raise InvalidForecastRunError(
                'Forecast target period cannot end before it starts.'
            )
        if sequence_window_months <= 0:
            raise InvalidForecastRunError('Forecast sequence window must be positive.')
        if not model_version.strip() or not artifact_version.strip():
            raise InvalidForecastRunError('Model and artifact versions are required.')
