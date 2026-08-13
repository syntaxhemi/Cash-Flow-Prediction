from calendar import monthrange
from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import TypedDict
from uuid import UUID

from database import IUnitOfWork
from database.models import FinancialTransactionModel
from domain.financial import TransactionDirection, TransactionType
from schemas.financial import (
    CounterpartyMonthlyReceivableCreateSchema,
    MonthlyCashflowAggregateCreateSchema,
)


class ReceivableData(TypedDict):
    invoice_total: Decimal
    amount_paid: Decimal
    delays: list[int]
    late_invoice_count: int


class MonthlyAggregationService:
    """Rebuild forecast-ready aggregates for an ingestion run."""

    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize the aggregation service.

        Args:
            uow: Unit of work used to read transactions and persist aggregates.
        """
        self._uow = uow

    async def rebuild_for_ingestion_run(
        self, enterprise_id: UUID, ingestion_run_id: UUID
    ) -> None:
        """Rebuild all periods touched by an ingestion run.

        Args:
            enterprise_id: Owning enterprise identifier.
            ingestion_run_id: Ingestion run whose transactions identify periods
                requiring recomputation.

        Notes:
            Each affected period is rebuilt from all normalized transactions in that
            period, making repeated ingestion idempotent.
        """
        transactions = await self._uow.financial_transactions.list_for_ingestion_run(
            enterprise_id, ingestion_run_id
        )
        periods = {
            _month_bounds(transaction.transaction_date) for transaction in transactions
        }
        for period_start, period_end in sorted(periods):
            period_transactions = (
                await self._uow.financial_transactions.list_for_period(
                    enterprise_id, period_start, period_end
                )
            )
            await self._rebuild_period(
                enterprise_id,
                ingestion_run_id,
                period_start,
                period_end,
                period_transactions,
            )

    async def _rebuild_period(
        self,
        enterprise_id: UUID,
        ingestion_run_id: UUID,
        period_start: date,
        period_end: date,
        transactions: list[FinancialTransactionModel],
    ) -> None:
        """Calculate and persist enterprise and counterparty period aggregates.

        Args:
            enterprise_id: Owning enterprise identifier.
            ingestion_run_id: Run recorded as the source of the derived aggregate.
            period_start: Inclusive first date of the calendar period.
            period_end: Inclusive last date of the calendar period.
            transactions: Normalized transactions within the period.
        """
        total_invoice_amount = Decimal(0)
        total_inflows = Decimal(0)
        total_outflows = Decimal(0)
        monthly_repayment = Decimal(0)
        total_payment_delay_days = Decimal(0)
        invoice_count = payment_count = 0
        receivables: defaultdict[UUID, ReceivableData] = defaultdict(
            lambda: {
                'invoice_total': Decimal(0),
                'amount_paid': Decimal(0),
                'delays': [],
                'late_invoice_count': 0,
            }
        )

        for transaction in transactions:
            if transaction.direction == TransactionDirection.INFLOW:
                total_inflows += transaction.amount
            else:
                total_outflows += transaction.amount

            if transaction.transaction_type == TransactionType.INVOICE:
                invoice_count += 1
                total_invoice_amount += transaction.amount

                if transaction.settlement_date is not None:
                    delay = (
                        transaction.settlement_date - transaction.transaction_date
                    ).days
                    total_payment_delay_days += Decimal(delay)

                if transaction.counterparty_id is not None:
                    data = receivables[transaction.counterparty_id]
                    data['invoice_total'] = data['invoice_total'] + transaction.amount
                    if transaction.settlement_date is not None:
                        delay = (
                            transaction.settlement_date - transaction.transaction_date
                        ).days
                        data['delays'].append(delay)
                        if delay > 0:
                            data['late_invoice_count'] = data['late_invoice_count'] + 1
                    elif str(transaction.status) == 'overdue':
                        data['late_invoice_count'] = data['late_invoice_count'] + 1

            if transaction.transaction_type == TransactionType.PAYMENT:
                payment_count += 1
                if transaction.counterparty_id is not None:
                    data = receivables[transaction.counterparty_id]
                    data['amount_paid'] = data['amount_paid'] + transaction.amount

            if transaction.transaction_type == TransactionType.LOAN_REPAYMENT:
                monthly_repayment += transaction.amount

        await self._uow.monthly_cashflow_aggregates.upsert(
            MonthlyCashflowAggregateCreateSchema(
                enterprise_id=enterprise_id,
                period_start=period_start,
                period_end=period_end,
                total_invoice_amount=total_invoice_amount,
                total_inflows=total_inflows,
                total_outflows=total_outflows,
                monthly_repayment=monthly_repayment,
                total_payment_delay_days=total_payment_delay_days,
                invoice_count=invoice_count,
                payment_count=payment_count,
                derived_from_run_id=ingestion_run_id,
            )
        )

        for counterparty_id, data in receivables.items():
            delays = data['delays']
            average_delay = (
                Decimal(sum(delays)) / Decimal(len(delays)) if delays else None
            )
            invoice_total = data['invoice_total']
            amount_paid = data['amount_paid']
            await self._uow.counterparty_monthly_receivables.upsert(
                CounterpartyMonthlyReceivableCreateSchema(
                    enterprise_id=enterprise_id,
                    counterparty_id=counterparty_id,
                    period_start=period_start,
                    period_end=period_end,
                    invoice_total=invoice_total,
                    amount_paid=amount_paid,
                    outstanding_amount=max(invoice_total - amount_paid, Decimal(0)),
                    average_payment_delay_days=average_delay,
                    late_invoice_count=data['late_invoice_count'],
                )
            )


def _month_bounds(value: date) -> tuple[date, date]:
    """Return inclusive first and last dates for a calendar month."""
    start = value.replace(day=1)
    return start, value.replace(day=monthrange(value.year, value.month)[1])
