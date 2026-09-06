from dataclasses import replace

import numpy as np

from ml.artifacts import ForecastArtifactMetadata
from ml.preparation.feature_preparation import PreparedForecastFeatures

MONETARY_TEMPORAL_FEATURES = frozenset(
    {
        'total_invoice_amount',
        'monthly_repayment',
        'total_inflows',
        'total_outflows',
    }
)
MONETARY_STATIC_FEATURES = frozenset(
    {
        'capex',
        'cogs',
        'current_assets',
        'current_liabilities',
        'fixed_assets',
        'long_term_liabilities',
    }
)


class ForecastCurrencyConverter:
    """Convert monetary forecast values to and from the artifact currency."""

    def to_training_currency(
        self,
        features: PreparedForecastFeatures,
        metadata: ForecastArtifactMetadata,
        input_currency: str,
    ) -> PreparedForecastFeatures:
        """Convert monetary input columns into the artifact training currency.

        Args:
            features: Unscaled features expressed in the enterprise currency.
            metadata: Artifact currency and feature-order contract.
            input_currency: ISO currency code used by the enterprise inputs.

        Returns:
            A copy of the features with only monetary columns converted.

        Raises:
            ValueError: If the input currency is unsupported by the artifact.
        """
        rate = self._rate(metadata, input_currency)
        if rate == 1.0:
            return features

        temporal = features.temporal.copy()
        static = features.static.copy()
        for index, feature in enumerate(metadata.temporal_features):
            if feature in MONETARY_TEMPORAL_FEATURES:
                temporal[:, index] /= rate
        for index, feature in enumerate(metadata.static_features):
            if feature in MONETARY_STATIC_FEATURES:
                static[:, index] /= rate
        return replace(features, temporal=temporal, static=static)

    def prediction_to_input_currency(
        self,
        prediction: float,
        metadata: ForecastArtifactMetadata,
        input_currency: str,
    ) -> float:
        """Convert a training-currency prediction to the enterprise currency.

        Args:
            prediction: Predicted cash flow in the artifact training currency.
            metadata: Artifact currency conversion contract.
            input_currency: ISO currency code requested by the enterprise.

        Returns:
            Prediction expressed in the enterprise currency.

        Raises:
            ValueError: If the input currency is unsupported by the artifact.
        """
        return prediction * self._rate(metadata, input_currency)

    @staticmethod
    def _rate(metadata: ForecastArtifactMetadata, input_currency: str) -> float:
        currency = input_currency.upper()
        try:
            rate = metadata.currency_units_per_training_unit[currency]
        except KeyError as error:
            raise ValueError(
                f'Artifact does not support forecast currency "{currency}".'
            ) from error
        if not np.isfinite(rate) or rate <= 0:
            raise ValueError(f'Artifact currency rate for "{currency}" is invalid.')
        return rate
