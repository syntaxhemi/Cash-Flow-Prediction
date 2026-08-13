from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from ml.artifacts import ForecastArtifactMetadata


@dataclass(frozen=True, slots=True)
class PreparedForecastFeatures:
    """Validated feature arrays ready for scaling and model inference."""

    temporal: np.ndarray
    static: np.ndarray


class ForecastFeaturePreparationService:
    """Build model-ordered arrays from named feature values."""

    def prepare(
        self,
        temporal_rows: Sequence[Mapping[str, float]],
        static_values: Mapping[str, float],
        metadata: ForecastArtifactMetadata,
    ) -> PreparedForecastFeatures:
        """Prepare feature arrays in artifact-defined order.

        Args:
            temporal_rows: Chronologically ordered monthly feature mappings.
            static_values: Static feature mapping for the enterprise snapshot.
            metadata: Loaded artifact metadata defining feature order and window size.

        Returns:
            Validated two-dimensional temporal and static arrays.

        Raises:
            ValueError: If rows, names, values, or dimensions are incompatible.
        """
        if len(temporal_rows) != metadata.sequence_length:
            raise ValueError(
                f'Expected {metadata.sequence_length} temporal rows; '
                f'received {len(temporal_rows)}.'
            )
        temporal = np.asarray(
            [
                [self._value(row, feature) for feature in metadata.temporal_features]
                for row in temporal_rows
            ],
            dtype=float,
        )
        static = np.asarray(
            [
                [
                    self._value(static_values, feature)
                    for feature in metadata.static_features
                ]
            ],
            dtype=float,
        )
        if not np.isfinite(temporal).all() or not np.isfinite(static).all():
            raise ValueError('Forecast features must contain only finite values.')
        return PreparedForecastFeatures(temporal=temporal, static=static)

    @staticmethod
    def _value(values: Mapping[str, float], feature: str) -> float:
        """Read one finite numeric feature value from a named mapping."""
        if feature not in values:
            raise ValueError(f'Missing required forecast feature "{feature}".')

        value = values[feature]

        if not isinstance(value, (int, float)):
            raise TypeError(f'Forecast feature "{feature}" must be numeric.')

        return float(value)
