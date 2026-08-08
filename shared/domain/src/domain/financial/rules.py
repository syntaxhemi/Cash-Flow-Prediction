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
    ) -> None:
        """Validate transaction amount, currency, and date ordering."""
        ...

    def validate_period(self, period_start: date, period_end: date) -> None:
        """Validate a financial period range."""
        ...

    def validate_receivable(
        self,
        *,
        invoice_total: Decimal,
        amount_paid: Decimal,
        outstanding_amount: Decimal,
    ) -> None:
        """Validate receivable amount consistency."""
        ...


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
        """Validate transaction amount, currency, and date ordering.

        Args:
            amount: Positive transaction amount.
            currency_code: Three-letter currency code.
            transaction_date: Transaction date.
            due_date: Optional due date.
            settlement_date: Optional settlement date.

        Raises:
            InvalidFinancialRecordError: If an invariant is violated.
        """
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
        """Validate that a financial period has a valid date range.

        Args:
            period_start: Inclusive period start.
            period_end: Inclusive period end.

        Raises:
            InvalidFinancialRecordError: If the end precedes the start.
        """
        if period_end < period_start:
            raise InvalidFinancialRecordError('Period end cannot precede period start.')

    def validate_receivable(
        self,
        *,
        invoice_total: Decimal,
        amount_paid: Decimal,
        outstanding_amount: Decimal,
    ) -> None:
        """Validate the accounting identity for outstanding receivables.

        Args:
            invoice_total: Total invoiced amount.
            amount_paid: Amount already paid.
            outstanding_amount: Remaining amount due.

        Raises:
            InvalidFinancialRecordError: If amounts are negative or inconsistent.
        """
        if min(invoice_total, amount_paid, outstanding_amount) < 0:
            raise InvalidFinancialRecordError('Receivable amounts cannot be negative.')
        if outstanding_amount != invoice_total - amount_paid:
            raise InvalidFinancialRecordError(
                'Outstanding amount must equal invoice total less amount paid.'
            )
