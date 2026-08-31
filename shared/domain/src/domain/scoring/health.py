from collections.abc import Mapping
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from enum import StrEnum


class HealthStatus(StrEnum):
    """Directional status bands for the health score."""

    COMFORTABLE = 'comfortable'
    AT_RISK = 'at_risk'
    CRITICAL = 'critical'


HEALTH_SCORE_FEATURES = (
    'credit_score',
    'failure_score',
    'debt_to_revenue_ratio',
    'missed_payments_number',
)

_HUNDRED = Decimal(100)
_MISSED_PAYMENTS_LIMIT = Decimal(5)
_SCORE_QUANTUM = Decimal('0.01')


def calculate_health_score(
    static_values: Mapping[str, Decimal | float | int],
) -> Decimal:
    """Calculate a bounded directional health score from static model features.

    Args:
            static_values: Static feature values used by the forecasting model. The
                    mapping must contain credit score, failure score, debt-to-revenue ratio,
                    and missed-payment count.

    Returns:
            A score from 0 to 100, rounded to two decimal places.

    Raises:
            ValueError: If a required feature is missing, invalid, or negative.

    Notes:
            Credit score and failure score are expected on a 0-to-1 scale. A
            debt-to-revenue ratio of 1 and five missed payments represent the risk
            limits for this directional index. This score is decision support and is
            not a covenant-compliance determination.
    """
    credit_score = _value(static_values, 'credit_score')
    failure_score = _value(static_values, 'failure_score')
    debt_to_revenue_ratio = _value(static_values, 'debt_to_revenue_ratio')
    missed_payments = _value(static_values, 'missed_payments_number')

    credit_component = _clamp(credit_score, Decimal(0), Decimal(1)) * _HUNDRED
    failure_component = (
        Decimal(1) - _clamp(failure_score, Decimal(0), Decimal(1))
    ) * _HUNDRED
    debt_component = (
        Decimal(1) - _clamp(debt_to_revenue_ratio, Decimal(0), Decimal(1))
    ) * _HUNDRED
    payments_component = (
        Decimal(1)
        - _clamp(missed_payments / _MISSED_PAYMENTS_LIMIT, Decimal(0), Decimal(1))
    ) * _HUNDRED

    score = (
        Decimal('0.30') * credit_component
        + Decimal('0.30') * failure_component
        + Decimal('0.25') * debt_component
        + Decimal('0.15') * payments_component
    )
    return score.quantize(_SCORE_QUANTUM, rounding=ROUND_HALF_UP)


def classify_health_score(score: Decimal | float) -> HealthStatus:
    """Map a health score to its directional status band.

    Args:
            score: Health score on a 0-to-100 scale.

    Returns:
            The corresponding health status.

    Raises:
            ValueError: If the score is non-finite or outside the 0-to-100 range.
    """
    numeric_score = _as_decimal(score, 'health_score')
    if numeric_score < 0 or numeric_score > _HUNDRED:
        raise ValueError('health_score must be between 0 and 100.')
    if numeric_score >= Decimal(70):
        return HealthStatus.COMFORTABLE
    if numeric_score >= Decimal(45):
        return HealthStatus.AT_RISK
    return HealthStatus.CRITICAL


def _value(static_values: Mapping[str, Decimal | float | int], feature: str) -> Decimal:
    if feature not in static_values:
        raise ValueError(f'Missing required health feature "{feature}".')
    return _as_decimal(static_values[feature], feature)


def _as_decimal(value: Decimal | float, name: str) -> Decimal:
    try:
        numeric_value = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f'{name} must be a finite numeric value.') from error
    if not numeric_value.is_finite() or numeric_value < 0:
        raise ValueError(f'{name} must be a finite non-negative value.')
    return numeric_value


def _clamp(value: Decimal, minimum: Decimal, maximum: Decimal) -> Decimal:
    return max(minimum, min(value, maximum))
