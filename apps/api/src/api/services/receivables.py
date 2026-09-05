from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from statistics import median
from typing import Literal
from uuid import UUID

from database import IUnitOfWork
from database.models import (
    CounterpartyMonthlyReceivableModel,
    FinancialTransactionModel,
)
from domain.exceptions import InvalidForecastRunError
from domain.financial import TransactionStatus, TransactionType
from domain.forecasting import ForecastStatus
from schemas.financial import (
    ReceivableItemSchema,
    ReceivableRecordSchema,
    ReceivablesFilterParams,
    ReceivablesListResponse,
    ReceivablesSummarySchema,
)


class ReceivablesService:
    """Provide forecast-scoped receivable details for the dashboard."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize the service.

        Args:
                uow: Unit of work used to load forecast and receivable data.
        """
        self._uow = uow

    async def get_for_forecast(
        self, enterprise_id: UUID, filters: ReceivablesFilterParams
    ) -> ReceivablesListResponse:
        """Return receivables supporting one completed forecast.

        Args:
                enterprise_id: Owning enterprise identifier.
                filters: Forecast and account-window filters.

        Returns:
                Counterparty receivable details, supporting invoice records, and summary data.

        Raises:
                InvalidForecastRunError: If the selected forecast is missing or incomplete.
        """
        forecast = await self._uow.forecasts.get_by_id_with_inputs(
            enterprise_id, filters.forecast_run_id
        )
        if forecast is None or forecast.enterprise_id != enterprise_id:
            raise InvalidForecastRunError(
                f'Forecast run "{filters.forecast_run_id}" does not belong to the enterprise.'
            )
        if forecast.status is not ForecastStatus.COMPLETED:
            raise InvalidForecastRunError(
                'Receivables require a completed baseline forecast.'
            )

        periods = sorted(forecast.periods, key=lambda period: period.sequence_index)
        if not periods:
            return ReceivablesListResponse(
                items=[],
                summary=ReceivablesSummarySchema(
                    total_outstanding=Decimal(0),
                    counterparty_count=0,
                    median_payment_delay_days=None,
                ),
            )

        aggregates = (
            await self._uow.counterparty_monthly_receivables.list_for_enterprise(
                enterprise_id,
                periods[0].monthly_cashflow_aggregate.period_start,
                periods[-1].monthly_cashflow_aggregate.period_end,
            )
        )
        latest_by_counterparty = self._latest_aggregates(aggregates)
        items: list[ReceivableItemSchema] = []
        reference_date = datetime.now(UTC).date()

        for aggregate in latest_by_counterparty.values():
            if aggregate.outstanding_amount <= 0:
                continue
            transactions = await self._uow.financial_transactions.list_for_counterparty(
                enterprise_id, aggregate.counterparty_id
            )
            records = [
                transaction
                for transaction in transactions
                if transaction.transaction_type is TransactionType.INVOICE
            ]
            allocations = await self._uow.invoice_payment_allocations.list_for_invoices(
                enterprise_id, [record.id for record in records]
            )
            paid_by_invoice: defaultdict[UUID, Decimal] = defaultdict(Decimal)
            paid_date_by_invoice: dict[UUID, date] = {}
            transactions_by_id = {
                transaction.id: transaction for transaction in transactions
            }
            for allocation in allocations:
                paid_by_invoice[allocation.invoice_id] += allocation.allocated_amount
                payment = transactions_by_id.get(allocation.payment_transaction_id)
                if payment is not None:
                    payment_date = payment.settlement_date or payment.transaction_date
                    current_date = paid_date_by_invoice.get(allocation.invoice_id)
                    if current_date is None or payment_date > current_date:
                        paid_date_by_invoice[allocation.invoice_id] = payment_date
            open_records = [
                record
                for record in records
                if self._is_open_record(record, paid_by_invoice[record.id])
            ]
            if not self._matches_filter(open_records, filters, reference_date):
                continue

            items.append(
                ReceivableItemSchema(
                    counterparty_id=aggregate.counterparty_id,
                    name=aggregate.counterparty.name,
                    counterparty_type=aggregate.counterparty.counterparty_type,
                    invoice_total=aggregate.invoice_total,
                    amount_paid=aggregate.amount_paid,
                    outstanding_amount=aggregate.outstanding_amount,
                    average_payment_delay_days=aggregate.average_payment_delay_days,
                    late_invoice_count=aggregate.late_invoice_count,
                    paid_on_time_percentage=self._paid_on_time_percentage(
                        records, paid_by_invoice, paid_date_by_invoice
                    ),
                    records=[
                        self._record_schema(
                            record, reference_date, paid_by_invoice[record.id]
                        )
                        for record in open_records
                    ],
                )
            )

        items.sort(key=lambda item: item.outstanding_amount, reverse=True)
        delays = [
            item.average_payment_delay_days
            for item in items
            if item.average_payment_delay_days is not None
        ]
        return ReceivablesListResponse(
            items=items,
            summary=ReceivablesSummarySchema(
                total_outstanding=sum(
                    (item.outstanding_amount for item in items), Decimal()
                ),
                counterparty_count=len(items),
                median_payment_delay_days=(
                    Decimal(str(median(delays))).quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP
                    )
                    if delays
                    else None
                ),
            ),
        )

    @staticmethod
    def _latest_aggregates(
        aggregates: list[CounterpartyMonthlyReceivableModel],
    ) -> dict[UUID, CounterpartyMonthlyReceivableModel]:
        """Select the latest materialized aggregate for each counterparty."""
        latest: dict[UUID, CounterpartyMonthlyReceivableModel] = {}
        for aggregate in aggregates:
            current = latest.get(aggregate.counterparty_id)
            if current is None or aggregate.period_end > current.period_end:
                latest[aggregate.counterparty_id] = aggregate
        return latest

    @staticmethod
    def _is_open_record(
        record: FinancialTransactionModel, amount_paid: Decimal
    ) -> bool:
        """Return whether an invoice is still part of the receivable balance."""
        return (
            record.settlement_date is None
            and record.status
            not in (
                TransactionStatus.SETTLED,
                TransactionStatus.CANCELLED,
            )
            and amount_paid < record.amount
        )

    @staticmethod
    def _matches_filter(
        records: list[FinancialTransactionModel],
        filters: ReceivablesFilterParams,
        reference_date: date,
    ) -> bool:
        """Return whether open records match the requested account filter."""
        if not records:
            return filters.account_filter == 'all'
        horizon_end = reference_date + timedelta(days=int(filters.horizon_days))
        has_overdue = any(
            ReceivablesService._inferred_status(record, reference_date)
            is TransactionStatus.OVERDUE
            for record in records
        )
        if filters.account_filter == 'overdue':
            return has_overdue
        if filters.account_filter == 'upcoming':
            return any(
                record.due_date is not None
                and reference_date <= record.due_date <= horizon_end
                for record in records
            )
        return True

    @staticmethod
    def _paid_on_time_percentage(
        records: list[FinancialTransactionModel],
        paid_by_invoice: dict[UUID, Decimal],
        paid_date_by_invoice: dict[UUID, date],
    ) -> Decimal | None:
        """Calculate the fully-paid-on-time percentage for invoice records."""
        eligible_count = 0
        on_time_count = 0
        for record in records:
            if record.due_date is None or paid_by_invoice[record.id] < record.amount:
                continue
            payment_date = record.settlement_date or paid_date_by_invoice.get(record.id)
            if payment_date is None:
                continue
            eligible_count += 1
            on_time_count += payment_date <= record.due_date
        if eligible_count == 0:
            return None
        return (
            Decimal(on_time_count) / Decimal(eligible_count) * Decimal(100)
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @staticmethod
    def _inferred_status(
        record: FinancialTransactionModel, reference_date: date
    ) -> TransactionStatus:
        """Infer invoice status from settlement and due dates."""
        if (
            record.settlement_date is not None
            or record.status is TransactionStatus.SETTLED
        ):
            return TransactionStatus.SETTLED
        if record.status is TransactionStatus.CANCELLED:
            return TransactionStatus.CANCELLED
        if record.due_date is not None:
            return (
                TransactionStatus.OVERDUE
                if record.due_date < reference_date
                else TransactionStatus.PENDING
            )
        return record.status

    @staticmethod
    def _record_schema(
        record: FinancialTransactionModel,
        reference_date: date,
        amount_paid: Decimal = Decimal(0),
    ) -> ReceivableRecordSchema:
        """Convert an invoice and its allocations into a supporting record.

        Args:
            record: Invoice transaction to serialize.
            reference_date: Date used to infer overdue versus pending.
            amount_paid: Total payment amount allocated to the invoice.

        Returns:
            Allocation-aware receivable record.
        """
        outstanding_amount = max(Decimal(0), record.amount - amount_paid)
        payment_status: Literal['unpaid', 'partially_paid', 'paid'] = (
            'paid'
            if outstanding_amount == 0
            else 'partially_paid'
            if amount_paid > 0
            else 'unpaid'
        )
        return ReceivableRecordSchema(
            id=record.id,
            reference_number=record.reference_number,
            issued_date=record.transaction_date,
            due_date=record.due_date,
            settlement_date=record.settlement_date,
            amount=record.amount,
            amount_paid=amount_paid,
            outstanding_amount=outstanding_amount,
            currency_code=record.currency_code,
            status=ReceivablesService._inferred_status(record, reference_date),
            payment_status=payment_status,
        )
