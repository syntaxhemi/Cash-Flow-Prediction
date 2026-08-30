from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, cast
from uuid import UUID

from domain.exceptions import (
    FinancialTransactionAlreadyExistsError,
    FinancialTransactionNotFoundError,
)
from domain.financial import TransactionDirection, TransactionStatus
from schemas.financial import (
    FinancialTransactionCreateSchema,
    FinancialTransactionFilterParams,
    FinancialTransactionUpdateSchema,
)
from sqlalchemy import case, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import FinancialTransactionModel


@dataclass(frozen=True, slots=True)
class FinancialTransactionPersistenceResult:
    """Summarize a transaction persistence batch."""

    inserted_count: int
    duplicate_count: int


@dataclass(slots=True)
class FinancialTransactionListResult:
    """Paginated financial transaction query result."""

    items: list[FinancialTransactionModel]
    total_count: int


@dataclass(frozen=True, slots=True)
class ExpectedCashflowResult:
    """Expected unsettled cash movements for a date range."""

    inflows: Decimal
    outflows: Decimal


class FinancialTransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an async database session.

        Args:
            session: Session used for persistence operations.
        """
        self._session = session

    async def create(
        self, payload: FinancialTransactionCreateSchema
    ) -> FinancialTransactionModel:
        """Create and persist one financial transaction.

        Args:
            payload: Validated transaction creation data.

        Returns:
            The persisted transaction model.

        Raises:
            FinancialTransactionAlreadyExistsError: If the source record already
                exists for the ingestion source.
        """
        values = payload.model_dump(
            exclude={
                'counterparty_external_key',
                'counterparty_name',
                'counterparty_type',
            }
        )
        transaction = FinancialTransactionModel(**values)
        self._session.add(transaction)

        try:
            await self._session.flush()

        except IntegrityError as error:
            if self._matches_constraint(
                error,
                'financial_transactions_ingestion_source_id_source_record_id_key',
                'uq_financial_transactions_ingestion_source_id_source_record_id',
            ):
                raise FinancialTransactionAlreadyExistsError(
                    f'Transaction with source record "{payload.source_record_id}" '
                    f'already exists for source "{payload.ingestion_source_id}".'
                ) from error
            raise

        await self._session.refresh(transaction)
        return transaction

    async def get_by_id(self, transaction_id: UUID) -> FinancialTransactionModel | None:
        """Return a transaction by identifier when it exists.

        Args:
            transaction_id: Transaction identifier to query.

        Returns:
            The matching transaction model, or ``None``.
        """
        result = await self._session.execute(
            select(FinancialTransactionModel).where(
                FinancialTransactionModel.id == transaction_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(
        self, transaction_id: UUID
    ) -> FinancialTransactionModel:
        """Return a transaction or raise when it is missing.

        Args:
            transaction_id: Transaction identifier to query.

        Returns:
            The matching transaction model.

        Raises:
            FinancialTransactionNotFoundError: If no transaction exists.
        """
        transaction = await self.get_by_id(transaction_id)
        if transaction is None:
            raise FinancialTransactionNotFoundError(
                f'Financial transaction "{transaction_id}" does not exist.'
            )
        return transaction

    async def list_transactions(
        self, enterprise_id: UUID, filters: FinancialTransactionFilterParams
    ) -> FinancialTransactionListResult:
        """Return paginated transactions for an enterprise.

        Args:
            enterprise_id: Owning enterprise identifier.
            filters: Transaction filters and pagination parameters.

        Returns:
            Matching transaction models and total count.
        """
        statement: Any = (
            select(FinancialTransactionModel)
            .where(FinancialTransactionModel.enterprise_id == enterprise_id)
            .order_by(
                FinancialTransactionModel.transaction_date.desc(),
                FinancialTransactionModel.id,
            )
            .limit(filters.limit)
            .offset(filters.offset)
        )
        count_statement = (
            select(func.count())
            .select_from(FinancialTransactionModel)
            .where(FinancialTransactionModel.enterprise_id == enterprise_id)
        )
        result = await self._session.execute(statement)
        total_count = (await self._session.execute(count_statement)).scalar_one()
        return FinancialTransactionListResult(
            items=list(result.scalars().all()), total_count=total_count
        )

    async def list_for_period(
        self, enterprise_id: UUID, period_start: date, period_end: date
    ) -> list[FinancialTransactionModel]:
        """Return all transactions dated within an inclusive calendar period.

        Args:
            enterprise_id: Owning enterprise identifier.
            period_start: Inclusive first transaction date.
            period_end: Inclusive last transaction date.

        Returns:
            Transactions ordered chronologically.
        """
        result = await self._session.execute(
            select(FinancialTransactionModel)
            .where(
                FinancialTransactionModel.enterprise_id == enterprise_id,
                FinancialTransactionModel.transaction_date >= period_start,
                FinancialTransactionModel.transaction_date <= period_end,
            )
            .order_by(
                FinancialTransactionModel.transaction_date,
                FinancialTransactionModel.id,
            )
        )
        return list(result.scalars().all())

    async def get_expected_cashflow(
        self, enterprise_id: UUID, period_start: date, period_end: date
    ) -> ExpectedCashflowResult:
        """Sum unsettled cash movements scheduled within a date range.

        Args:
            enterprise_id: Owning enterprise identifier.
            period_start: Inclusive expected movement date.
            period_end: Inclusive expected movement date.

        Returns:
            Expected inflow and outflow totals. Transactions without a due date
            use their transaction date.
        """
        expected_date = func.coalesce(
            FinancialTransactionModel.due_date,
            FinancialTransactionModel.transaction_date,
        )
        statement = select(
            func.coalesce(
                func.sum(
                    case(
                        (
                            FinancialTransactionModel.direction
                            == TransactionDirection.INFLOW,
                            FinancialTransactionModel.amount,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label('inflows'),
            func.coalesce(
                func.sum(
                    case(
                        (
                            FinancialTransactionModel.direction
                            == TransactionDirection.OUTFLOW,
                            FinancialTransactionModel.amount,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label('outflows'),
        ).where(
            FinancialTransactionModel.enterprise_id == enterprise_id,
            FinancialTransactionModel.status.in_(
                (TransactionStatus.PENDING, TransactionStatus.OVERDUE)
            ),
            expected_date >= period_start,
            expected_date <= period_end,
        )
        result = await self._session.execute(statement)
        row = result.one()
        return ExpectedCashflowResult(
            inflows=row.inflows,
            outflows=row.outflows,
        )

    async def list_for_ingestion_run(
        self, enterprise_id: UUID, ingestion_run_id: UUID
    ) -> list[FinancialTransactionModel]:
        """Return transactions persisted by one ingestion run.

        Args:
            enterprise_id: Owning enterprise identifier.
            ingestion_run_id: Ingestion run identifier.

        Returns:
            Transactions persisted for the specified run.
        """
        result = await self._session.execute(
            select(FinancialTransactionModel).where(
                FinancialTransactionModel.enterprise_id == enterprise_id,
                FinancialTransactionModel.ingestion_run_id == ingestion_run_id,
            )
        )
        return list(result.scalars().all())

    async def update(
        self, transaction_id: UUID, payload: FinancialTransactionUpdateSchema
    ) -> FinancialTransactionModel:
        """Update an existing financial transaction.

        Args:
            transaction_id: Transaction identifier to update.
            payload: Validated transaction fields to change.

        Returns:
            The updated transaction model.

        Raises:
            FinancialTransactionNotFoundError: If no transaction exists.
        """
        transaction = await self.get_by_id_or_raise(transaction_id)

        for field_name, field_value in payload.model_dump(exclude_unset=True).items():
            setattr(transaction, field_name, field_value)

        await self._session.flush()
        await self._session.refresh(transaction)
        return transaction

    async def create_many(
        self, payloads: list[FinancialTransactionCreateSchema]
    ) -> FinancialTransactionPersistenceResult:
        """Persist a transaction batch idempotently.

        Args:
            payloads: Canonical transaction persistence payloads.

        Returns:
            Inserted and duplicate transaction counts.
        """
        if not payloads:
            return FinancialTransactionPersistenceResult(0, 0)

        values = [
            payload.model_dump(
                exclude={
                    'counterparty_external_key',
                    'counterparty_name',
                    'counterparty_type',
                }
            )
            for payload in payloads
        ]
        statement = insert(FinancialTransactionModel).values(values)
        statement = statement.on_conflict_do_nothing(
            index_elements=['ingestion_source_id', 'source_record_id']
        )
        result = cast(CursorResult[Any], await self._session.execute(statement))
        inserted_count = result.rowcount or 0
        return FinancialTransactionPersistenceResult(
            inserted_count=inserted_count,
            duplicate_count=len(payloads) - inserted_count,
        )

    @staticmethod
    def _matches_constraint(error: IntegrityError, *constraint_names: str) -> bool:
        """Return whether an integrity error references a known constraint.

        Args:
            error: Integrity error raised by the database.
            *constraint_names: Constraint names to match.

        Returns:
            ``True`` when the database error references one of the constraints.
        """
        error_message = str(error.orig)
        return any(name in error_message for name in constraint_names)
