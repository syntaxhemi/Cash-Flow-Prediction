from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import InvoicePaymentAllocationModel


class InvoicePaymentAllocationRepository:
    """Read invoice-level payment allocations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

        Args:
            session: Session used for database reads.
        """
        self._session = session

    async def list_for_invoices(
        self, enterprise_id: UUID, invoice_ids: list[UUID]
    ) -> list[InvoicePaymentAllocationModel]:
        """Return allocations for the requested enterprise invoices.

        Args:
            enterprise_id: Owning enterprise identifier.
            invoice_ids: Invoice transaction identifiers to inspect.

        Returns:
            Allocation rows ordered by invoice and creation time.
        """
        if not invoice_ids:
            return []
        result = await self._session.execute(
            select(InvoicePaymentAllocationModel)
            .where(
                InvoicePaymentAllocationModel.enterprise_id == enterprise_id,
                InvoicePaymentAllocationModel.invoice_id.in_(invoice_ids),
            )
            .order_by(
                InvoicePaymentAllocationModel.invoice_id,
                InvoicePaymentAllocationModel.created_at,
            )
        )
        return list(result.scalars().all())
