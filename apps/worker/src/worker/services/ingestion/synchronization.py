from datetime import UTC, datetime
from uuid import UUID

from database import IUnitOfWork
from domain.exceptions import DomainError
from domain.ingestion import IngestionStatus
from integrations import (
    IngestionAdapterContext,
    IngestionAdapterRegistry,
)
from integrations.exceptions import IntegrationAdapterError
from schemas.financial import CounterpartyCreateSchema, FinancialTransactionCreateSchema
from schemas.ingestion import IngestionRunUpdateSchema, IngestionSourceUpdateSchema
from sqlalchemy.exc import SQLAlchemyError


class IngestionSynchronizationService:
    """Execute one source synchronization command."""

    def __init__(self, uow: IUnitOfWork, registry: IngestionAdapterRegistry) -> None:
        """Initialize synchronization dependencies.

        Args:
            uow: Unit of work for the synchronization transaction.
            registry: Registry used to resolve the source adapter.
        """
        self._uow = uow
        self._registry = registry

    async def execute(self, fields: dict[str, str]) -> None:
        """Process one Redis synchronization command.

        Args:
            fields: Stream fields containing run, enterprise, source, and cursor IDs.
        """
        run_id = UUID(fields['run_id'])
        enterprise_id = UUID(fields['enterprise_id'])
        source_id = UUID(fields['ingestion_source_id'])

        await self._uow.ingestion_runs.get_by_id_or_raise(run_id)

        source = await self._uow.ingestion_sources.get_active_by_id_or_raise(source_id)
        credential = await self._uow.ingestion_source_credentials.get_active_for_source(
            source_id
        )
        adapter = self._registry.get_adapter(source.source_key)
        cursor = self._parse_cursor(fields.get('since'))
        context = IngestionAdapterContext(
            enterprise_id=enterprise_id,
            ingestion_source_id=source_id,
            ingestion_run_id=run_id,
            configuration=credential.config_json,
            secret_ref=credential.secret_ref,
            cursor=cursor,
        )

        try:
            await self._uow.ingestion_runs.update(
                run_id,
                IngestionRunUpdateSchema(
                    status=IngestionStatus.RUNNING, started_at=datetime.now(UTC)
                ),
            )
            await adapter.validate_configuration(context)
            received = processed = failed = 0

            async for raw_record in adapter.fetch_records(context):
                received += 1
                try:
                    record = adapter.translate_record(context, raw_record)
                    counterparty_id = None
                    if (
                        record.counterparty_external_key is not None
                        and record.counterparty_name is not None
                        and record.counterparty_type is not None
                    ):
                        counterparty = (
                            await self._uow.counterparties.get_by_external_key(
                                enterprise_id, record.counterparty_external_key
                            )
                        )
                        if counterparty is None:
                            counterparty = await self._uow.counterparties.create(
                                enterprise_id,
                                CounterpartyCreateSchema(
                                    external_key=record.counterparty_external_key,
                                    name=record.counterparty_name,
                                    counterparty_type=record.counterparty_type,
                                ),
                            )
                        counterparty_id = counterparty.id
                    await self._uow.financial_transactions.create_many(
                        [
                            FinancialTransactionCreateSchema(
                                enterprise_id=enterprise_id,
                                ingestion_source_id=source_id,
                                ingestion_run_id=run_id,
                                counterparty_id=counterparty_id,
                                transaction_type=record.transaction_type,
                                transaction_date=record.transaction_date,
                                due_date=record.due_date,
                                settlement_date=record.settlement_date,
                                amount=record.amount,
                                currency_code=record.currency_code,
                                direction=record.direction,
                                status=record.status,
                                reference_number=record.reference_number,
                                description=record.description,
                                source_record_id=record.source_record_id,
                                source_payload_hash=record.source_payload_hash,
                            )
                        ]
                    )
                    processed += 1

                except IntegrationAdapterError:
                    failed += 1

            now = datetime.now(UTC)

            await self._uow.ingestion_runs.update(
                run_id,
                IngestionRunUpdateSchema(
                    status=IngestionStatus.COMPLETED,
                    finished_at=now,
                    records_received=received,
                    records_processed=processed,
                    records_failed=failed,
                ),
            )
            await self._uow.ingestion_sources.update(
                source_id, IngestionSourceUpdateSchema(last_synced_at=now)
            )
            await self._uow.commit()

        except (DomainError, IntegrationAdapterError, SQLAlchemyError) as error:
            await self._uow.rollback()
            await self._uow.ingestion_runs.update(
                run_id,
                IngestionRunUpdateSchema(
                    status=IngestionStatus.FAILED,
                    finished_at=datetime.now(UTC),
                    error_summary=str(error)[:2000],
                ),
            )
            await self._uow.commit()

    @staticmethod
    def _parse_cursor(value: str | None) -> datetime | None:
        """Parse an optional ISO-8601 synchronization cursor."""
        if not value:
            return None
        return datetime.fromisoformat(value)
