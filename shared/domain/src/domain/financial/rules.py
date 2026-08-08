from datetime import date
from decimal import Decimal
from typing import Protocol

from domain.exceptions import InvalidFinancialRecordError


class IFinancialRules(Protocol):
    def validate_transaction(
        self,
        *,
        amount: Decimal,
        currency_code: str,
        transaction_date: date,
        due_date: date | None,
        settlement_date: date | None,
    ) -> None: ...

    def validate_period(self, period_start: date, period_end: date) -> None: ...

    def validate_receivable(
        self,
        *,
        invoice_total: Decimal,
        amount_paid: Decimal,
        outstanding_amount: Decimal,
    ) -> None: ...


class DefaultFinancialRules:
    def validate_transaction(
        self,
        *,
        amount: Decimal,
        currency_code: str,
        transaction_date: date,
        due_date: date | None,
        settlement_date: date | None,
    ) -> None:
        if amount <= 0:
            raise InvalidFinancialRecordError('Transaction amount must be positive.')
        if len(currency_code) != 3 or not currency_code.isupper():
            raise InvalidFinancialRecordError(
                'Currency code must be a three-letter uppercase code.'
            )
        if due_date is not None and due_date < transaction_date:
            raise InvalidFinancialRecordError(
                'Due date cannot precede transaction date.'
            )
        if settlement_date is not None and settlement_date < transaction_date:
            raise InvalidFinancialRecordError(
                'Settlement date cannot precede transaction date.'
            )

    def validate_period(self, period_start: date, period_end: date) -> None:
        if period_end < period_start:
            raise InvalidFinancialRecordError('Period end cannot precede period start.')

    def validate_receivable(
        self,
        *,
        invoice_total: Decimal,
        amount_paid: Decimal,
        outstanding_amount: Decimal,
    ) -> None:
        if min(invoice_total, amount_paid, outstanding_amount) < 0:
            raise InvalidFinancialRecordError('Receivable amounts cannot be negative.')
        if outstanding_amount != invoice_total - amount_paid:
            raise InvalidFinancialRecordError(
                'Outstanding amount must equal invoice total less amount paid.'
            )
