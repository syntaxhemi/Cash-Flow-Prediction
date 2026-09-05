from decimal import Decimal

from api.services.forecasting.counterfactual import CounterfactualContext
from api.services.forecasting.mitigation import LiquidityMitigationService
from api.services.forecasting.trapped_liquidity import (
    TrappedLiquiditySimulationService,
)
from domain.simulation import LiquidityMitigationProfile, RecommendationActionType


def _context() -> CounterfactualContext:
    rows = [
        {
            'total_invoice_amount': 1000.0,
            'payment_delay': 10.0,
            'monthly_repayment': 300.0,
            'total_inflows': 900.0,
            'total_outflows': 600.0,
        }
        for _ in range(6)
    ]
    return CounterfactualContext(
        temporal_rows=rows,
        static_values={
            'capex': 1200.0,
            'cogs': 0.0,
            'current_assets': 0.0,
            'current_liabilities': 0.0,
            'fixed_assets': 0.0,
            'long_term_liabilities': 0.0,
            'credit_score': 0.7,
            'failure_score': 0.2,
            'debt_to_revenue_ratio': 0.3,
            'missed_payments_number': 0.0,
        },
        baseline_prediction=Decimal(300),
        solvency_buffer=Decimal(500),
    )


def test_mitigation_candidates_update_cash_outflows_consistently() -> None:
    candidates = LiquidityMitigationService._build_candidates(
        _context(), LiquidityMitigationProfile.STANDARD
    )
    capex = next(
        item
        for item in candidates
        if item.action_type is RecommendationActionType.DELAY_CAPEX
    )
    repayment = next(
        item
        for item in candidates
        if item.action_type is RecommendationActionType.ADJUST_REPAYMENT
        and item.recommended_value == Decimal('150.0')
    )

    assert capex.temporal_patch[5]['total_outflows'] == Decimal(500)
    assert repayment.temporal_patch[5]['monthly_repayment'] == Decimal('150.0')
    assert repayment.temporal_patch[5]['total_outflows'] == Decimal('450.0')


def test_delayed_inflows_are_proportional_and_bounded() -> None:
    simulated = TrappedLiquiditySimulationService._simulated_inflows(
        baseline_inflows=Decimal(900),
        invoice_amount=Decimal(1000),
        outstanding_amount=Decimal(600),
        delay_days=Decimal(15),
    )
    fully_delayed = TrappedLiquiditySimulationService._simulated_inflows(
        baseline_inflows=Decimal(400),
        invoice_amount=Decimal(1000),
        outstanding_amount=Decimal(600),
        delay_days=Decimal(60),
    )

    assert simulated == Decimal(600)
    assert fully_delayed == Decimal(0)
