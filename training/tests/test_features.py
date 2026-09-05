import pandas as pd
import pytest
from training.features import _normalize_score


def test_normalize_score_converts_research_scale_to_runtime_scale() -> None:
    frame = pd.DataFrame({'credit_score': [0, 500, 1000]})

    _normalize_score(frame, 'credit_score', 1000)

    assert frame['credit_score'].tolist() == [0.0, 0.5, 1.0]


def test_normalize_score_preserves_already_normalized_values() -> None:
    frame = pd.DataFrame({'failure_score': [0.0, 0.5, 1.0]})

    _normalize_score(frame, 'failure_score', 100)

    assert frame['failure_score'].tolist() == [0.0, 0.5, 1.0]


def test_normalize_score_rejects_values_outside_source_contract() -> None:
    frame = pd.DataFrame({'failure_score': [101]})

    with pytest.raises(ValueError, match='failure_score must be between'):
        _normalize_score(frame, 'failure_score', 100)
