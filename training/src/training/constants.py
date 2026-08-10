"""Canonical feature names used by training and inference."""

TEMPORAL_FEATURES = [
    'total_invoice_amount',
    'payment_delay',
    'monthly_repayment',
    'total_inflows',
    'total_outflows',
]

STATIC_FEATURES = [
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
]
