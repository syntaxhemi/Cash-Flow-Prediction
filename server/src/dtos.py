from pydantic import BaseModel

class SequenceInput(BaseModel):
    total_invoice_amount: float
    payment_delay: int
    monthly_repayment: float
    total_inflows: float
    total_outflows: float

class StaticInput(BaseModel):
    capex: float
    cogs: float
    current_assets: float
    current_liabilities: float
    fixed_assets: float
    long_term_liabilities: float
    credit_score: float
    failure_score: float
    debt_to_revenue_ratio: float
    missed_payments_number: float

class InferenceRequest(BaseModel):
    seq_input: SequenceInput
    static_input: StaticInput

class InferenceResponse(BaseModel):
    net_cash_flow: float
    