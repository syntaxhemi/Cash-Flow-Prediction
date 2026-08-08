from enum import StrEnum


class TransactionType(StrEnum):
    INVOICE = 'invoice'
    PAYMENT = 'payment'
    LOAN_REPAYMENT = 'loan_repayment'
    EXPENSE = 'expense'
    DEPOSIT = 'deposit'
    ADJUSTMENT = 'adjustment'


class TransactionDirection(StrEnum):
    INFLOW = 'inflow'
    OUTFLOW = 'outflow'


class TransactionStatus(StrEnum):
    PENDING = 'pending'
    SETTLED = 'settled'
    OVERDUE = 'overdue'
    CANCELLED = 'cancelled'


class EntryMode(StrEnum):
    SOURCE = 'source'
    MANUAL = 'manual'
    ADJUSTED = 'adjusted'
