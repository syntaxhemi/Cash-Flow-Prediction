from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
from ml.artifacts import ForecastArtifactMetadata, LoadedForecastArtifacts
from ml.inference import ForecastInferenceService
from ml.preparation import ForecastCurrencyConverter, PreparedForecastFeatures
from sklearn.preprocessing import StandardScaler
from torch import nn


class _ConstantModel(nn.Module):
    def forward(
        self, input_sequence: torch.Tensor, input_static: torch.Tensor
    ) -> torch.Tensor:
        del input_static
        return torch.full((input_sequence.shape[0], 1), 10.0)


def _artifacts(model_weight: float) -> LoadedForecastArtifacts:
    temporal_scaler = StandardScaler().fit(np.zeros((2, 5)))
    static_scaler = StandardScaler().fit(np.zeros((2, 10)))
    metadata = ForecastArtifactMetadata(
        model_version='test',
        artifact_version=2,
        training_run_name='test',
        created_at=datetime.now(UTC),
        sequence_length=6,
        temporal_features=[
            'total_invoice_amount',
            'payment_delay',
            'monthly_repayment',
            'total_inflows',
            'total_outflows',
        ],
        static_features=[
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
        ],
        label_column='net_cash_flow',
        sequence_input_size=5,
        static_input_size=10,
        persistence_model_weight=model_weight,
        persistence_strategy='none' if model_weight == 1.0 else 'sequence_mean',
        model_zscore_limit=200.0,
        training_currency='GBP',
        currency_units_per_training_unit={'GBP': 1.0, 'INR': 100.0},
        artifact_files={},
    )
    return LoadedForecastArtifacts(
        run_directory=Path('.'),
        metadata=metadata,
        model=_ConstantModel(),  # type: ignore[arg-type]
        temporal_scaler=temporal_scaler,
        static_scaler=static_scaler,
        target_scaler=None,
    )


def test_prediction_blends_model_with_sequence_mean_cashflow() -> None:
    temporal = np.asarray(
        [[0.0, 0.0, 0.0, inflow, 20.0] for inflow in (80, 100, 120, 140, 160, 180)]
    )
    features = PreparedForecastFeatures(
        temporal=temporal,
        static=np.zeros((1, 10)),
    )

    prediction = ForecastInferenceService().predict(features, _artifacts(0.5))

    assert prediction.predicted_net_cashflow == 60.0


def test_model_only_artifact_remains_backward_compatible() -> None:
    features = PreparedForecastFeatures(
        temporal=np.zeros((6, 5)),
        static=np.zeros((1, 10)),
    )

    prediction = ForecastInferenceService().predict(features, _artifacts(1.0))

    assert prediction.predicted_net_cashflow == 10.0


def test_extreme_scaled_inputs_fall_back_to_persistence_forecast() -> None:
    features = PreparedForecastFeatures(
        temporal=np.asarray([[0.0, 0.0, 0.0, 1000.0, 900.0] for _ in range(6)]),
        static=np.zeros((1, 10)),
    )

    prediction = ForecastInferenceService().predict(features, _artifacts(0.675))

    assert prediction.predicted_net_cashflow == 100.0


def test_inr_inputs_and_prediction_are_converted_through_gbp() -> None:
    features = PreparedForecastFeatures(
        temporal=np.asarray(
            [
                [0.0, 10.0, 0.0, inflow, 2000.0]
                for inflow in (8000, 10000, 12000, 14000, 16000, 18000)
            ]
        ),
        static=np.zeros((1, 10)),
    )

    prediction = ForecastInferenceService().predict(
        features, _artifacts(0.5), input_currency='INR'
    )

    assert prediction.predicted_net_cashflow == 6000.0


def test_currency_conversion_leaves_non_monetary_features_unchanged() -> None:
    features = PreparedForecastFeatures(
        temporal=np.asarray([[1000.0, 17.0, 3000.0, 5000.0, 2000.0]]),
        static=np.asarray(
            [[1000.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0, 0.78, 0.18, 0.42, 2.0]]
        ),
    )

    converted = ForecastCurrencyConverter().to_training_currency(
        features, _artifacts(1.0).metadata, 'INR'
    )

    np.testing.assert_allclose(converted.temporal, [[10.0, 17.0, 30.0, 50.0, 20.0]])
    np.testing.assert_allclose(
        converted.static,
        [[10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 0.78, 0.18, 0.42, 2.0]],
    )
