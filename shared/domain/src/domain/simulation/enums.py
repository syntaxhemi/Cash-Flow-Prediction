from enum import StrEnum


class SimulationType(StrEnum):
    HEALTH_DELTA = 'health_delta'
    TRAPPED_LIQUIDITY = 'trapped_liquidity'
    LIQUIDITY_MITIGATION = 'liquidity_mitigation'


class HealthDeltaProfile(StrEnum):
    """Server-defined sensitivity profile for health delta simulation."""

    CONSERVATIVE = 'conservative'
    STANDARD = 'standard'
    STRESS = 'stress'
    CUSTOM = 'custom'


class LiquidityMitigationProfile(StrEnum):
    """Server-defined intervention range for mitigation recommendations."""

    CONSERVATIVE = 'conservative'
    STANDARD = 'standard'
    STRESS = 'stress'


class SimulationStatus(StrEnum):
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'


class RecommendationActionType(StrEnum):
    DELAY_CAPEX = 'delay_capex'
    REDUCE_OUTFLOWS = 'reduce_outflows'
    ADJUST_REPAYMENT = 'adjust_repayment'
    OTHER = 'other'
