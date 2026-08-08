from enum import StrEnum


class SimulationType(StrEnum):
    HEALTH_DELTA = 'health_delta'
    TRAPPED_LIQUIDITY = 'trapped_liquidity'
    LIQUIDITY_MITIGATION = 'liquidity_mitigation'


class SimulationStatus(StrEnum):
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'


class RecommendationActionType(StrEnum):
    DELAY_CAPEX = 'delay_capex'
    REDUCE_CAPEX = 'reduce_capex'
    ADJUST_REPAYMENT = 'adjust_repayment'
    OTHER = 'other'
