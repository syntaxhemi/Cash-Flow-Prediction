from enum import StrEnum


class ForecastRunType(StrEnum):
    BASELINE = 'baseline'
    SCHEDULED_BASELINE = 'scheduled_baseline'
    AD_HOC_BASELINE = 'ad_hoc_baseline'


class ForecastStatus(StrEnum):
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
