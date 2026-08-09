import hashlib
import json
from collections.abc import AsyncIterator, Mapping
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import quote

import httpx
from domain.enterprise import CounterpartyType
from domain.financial import TransactionDirection, TransactionStatus, TransactionType

from integrations.exceptions import (
    IntegrationConfigurationError,
    IntegrationRecordTranslationError,
    IntegrationTransportError,
)
from integrations.models import (
    CanonicalTransactionRecord,
    IngestionAdapterContext,
    RawIngestionRecord,
)


class ERPNextAdapter:
    """Translate ERPNext accounting records into canonical transactions."""

    _SUPPORTED_DOCTYPES = (
        'Sales Invoice',
        'Purchase Invoice',
        'Payment Entry',
        'Journal Entry',
    )

    @property
    def source_key(self) -> str:
        """Return the stable ERPNext source key."""
        return 'erpnext'

    async def validate_configuration(self, context: IngestionAdapterContext) -> None:
        """Validate ERPNext connection configuration and credentials.

        Args:
            context: Source and synchronization configuration.

        Raises:
            IntegrationConfigurationError: If required values are invalid.
        """
        base_url = context.configuration.get('base_url')
        if not isinstance(base_url, str) or not base_url.strip():
            raise IntegrationConfigurationError(
                'ERPNext configuration requires a non-empty base_url.'
            )

        try:
            parsed_url = httpx.URL(base_url)

        except Exception as error:
            raise IntegrationConfigurationError(
                'ERPNext base_url must be a valid URL.'
            ) from error

        if parsed_url.scheme not in {'http', 'https'} or parsed_url.host is None:
            raise IntegrationConfigurationError(
                'ERPNext base_url must use HTTP or HTTPS and include a host.'
            )

        self._credentials(context.secret_ref)
        page_size = context.configuration.get('page_size', 100)

        if not isinstance(page_size, int) or not 1 <= page_size <= 500:
            raise IntegrationConfigurationError(
                'ERPNext page_size must be an integer between 1 and 500.'
            )

    async def fetch_records(
        self, context: IngestionAdapterContext
    ) -> AsyncIterator[RawIngestionRecord]:
        """Yield supported records from ERPNext using paginated requests.

        Args:
            context: Source and synchronization configuration.

        Yields:
            Raw ERPNext accounting records.
        """
        await self.validate_configuration(context)

        base_url = str(context.configuration['base_url']).rstrip('/')
        page_size = int(context.configuration.get('page_size', 100))
        timeout = float(context.configuration.get('timeout_seconds', 30))
        headers = self._headers(context.secret_ref)

        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            for doctype in self._SUPPORTED_DOCTYPES:
                start = 0
                while True:
                    params: dict[str, Any] = {
                        'fields': json.dumps(['*']),
                        'limit_page_length': page_size,
                        'limit_start': start,
                    }
                    if context.cursor is not None:
                        params['filters'] = json.dumps(
                            [['posting_date', '>=', context.cursor.date().isoformat()]]
                        )
                    payload = await self._get_page(client, base_url, doctype, params)
                    records = payload.get('data')

                    if not isinstance(records, list):
                        raise IntegrationTransportError(
                            f'ERPNext returned an invalid response for {doctype}.'
                        )

                    for record in records:
                        if isinstance(record, dict) and record.get('name'):
                            yield RawIngestionRecord(
                                source_record_id=f'{doctype}:{record["name"]}',
                                payload={'_doctype': doctype, **record},
                            )

                    if len(records) < page_size:
                        break

                    start += page_size

    def translate_record(
        self,
        context: IngestionAdapterContext,
        record: RawIngestionRecord,
    ) -> CanonicalTransactionRecord:
        """Translate one ERPNext record into a canonical transaction.

        Args:
            context: Source and synchronization configuration.
            record: Raw ERPNext record.

        Returns:
            Canonical transaction data.

        Raises:
            IntegrationRecordTranslationError: If required fields are invalid.
        """
        doctype = record.payload.get('_doctype')
        if not isinstance(doctype, str):
            raise IntegrationRecordTranslationError(
                f'ERPNext record "{record.source_record_id}" has no document type.'
            )

        transaction_type, direction, amount_key = self._mapping_for(doctype, record)
        amount = self._decimal(record.payload.get(amount_key), amount_key, record)
        transaction_date = self._parse_date(record.payload.get('posting_date'), record)
        currency_code = self._currency(record.payload, context)
        counterparty_key, counterparty_name, counterparty_type = self._counterparty(
            record.payload, doctype
        )

        return CanonicalTransactionRecord(
            source_record_id=record.source_record_id,
            transaction_type=transaction_type,
            transaction_date=transaction_date,
            amount=amount,
            currency_code=currency_code,
            direction=direction,
            status=self._status(record.payload, doctype),
            due_date=self._optional_date(record.payload.get('due_date'), record),
            settlement_date=self._optional_date(
                record.payload.get('clearance_date'), record
            ),
            counterparty_external_key=counterparty_key,
            counterparty_name=counterparty_name,
            counterparty_type=counterparty_type,
            reference_number=record.payload.get('name'),
            description=record.payload.get('remarks') or record.payload.get('title'),
            source_payload_hash=self._payload_hash(record.payload),
        )

    async def _get_page(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        doctype: str,
        params: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Fetch one ERPNext document page."""
        try:
            response = await client.get(
                f'{base_url}/api/resource/{quote(doctype, safe="")}', params=params
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise IntegrationTransportError(
                f'ERPNext request failed for document type "{doctype}".'
            ) from error

        if not isinstance(payload, dict):
            raise IntegrationTransportError('ERPNext returned a non-object response.')

        return payload

    @staticmethod
    def _credentials(secret_ref: str) -> tuple[str, str]:
        """Parse an ERPNext API key and secret from the stored credential."""
        api_key, separator, api_secret = secret_ref.partition(':')
        if not separator or not api_key or not api_secret:
            raise IntegrationConfigurationError(
                'ERPNext secret_ref must use the "api_key:api_secret" format.'
            )
        return api_key, api_secret

    @classmethod
    def _headers(cls, secret_ref: str) -> dict[str, str]:
        """Build ERPNext token authentication headers."""
        api_key, api_secret = cls._credentials(secret_ref)
        return {'Authorization': f'token {api_key}:{api_secret}'}

    @staticmethod
    def _mapping_for(
        doctype: str, record: RawIngestionRecord
    ) -> tuple[TransactionType, TransactionDirection, str]:
        """Return canonical type, direction, and amount field for a document."""
        if doctype == 'Sales Invoice':
            return TransactionType.INVOICE, TransactionDirection.INFLOW, 'grand_total'
        if doctype == 'Purchase Invoice':
            return TransactionType.INVOICE, TransactionDirection.OUTFLOW, 'grand_total'
        if doctype == 'Payment Entry':
            payment_type = record.payload.get('payment_type')
            direction = (
                TransactionDirection.INFLOW
                if payment_type == 'Receive'
                else TransactionDirection.OUTFLOW
            )
            return TransactionType.PAYMENT, direction, 'paid_amount'
        if doctype == 'Journal Entry':
            return (
                TransactionType.ADJUSTMENT,
                TransactionDirection.OUTFLOW,
                'total_debit',
            )
        raise IntegrationRecordTranslationError(
            f'ERPNext document type "{doctype}" is not supported.'
        )

    @staticmethod
    def _decimal(value: object, field_name: str, record: RawIngestionRecord) -> Decimal:
        """Parse a positive financial amount from a source record."""
        try:
            amount = Decimal(str(value))

        except (InvalidOperation, ValueError):
            raise IntegrationRecordTranslationError(
                f'ERPNext record "{record.source_record_id}" has an invalid '
                f'{field_name} amount.'
            ) from None

        if amount <= 0:
            raise IntegrationRecordTranslationError(
                f'ERPNext record "{record.source_record_id}" must have a positive '
                'amount.'
            )

        return amount

    @staticmethod
    def _parse_date(value: object, record: RawIngestionRecord) -> date:
        """Parse a required ISO date from a source record."""
        if not isinstance(value, str):
            raise IntegrationRecordTranslationError(
                f'ERPNext record "{record.source_record_id}" has no posting date.'
            )

        try:
            return date.fromisoformat(value[:10])
        except ValueError as ve:
            raise IntegrationRecordTranslationError(
                f'ERPNext record "{record.source_record_id}" has an invalid posting date.'
            ) from ve

    @classmethod
    def _optional_date(cls, value: object, record: RawIngestionRecord) -> date | None:
        """Parse an optional ISO date from a source record."""
        if value is None or value == '':
            return None
        return cls._parse_date(value, record)

    @staticmethod
    def _currency(payload: Mapping[str, Any], context: IngestionAdapterContext) -> str:
        """Return a validated three-letter currency code."""
        value = payload.get('currency') or payload.get('company_currency')
        value = value or context.configuration.get('currency_code')
        if not isinstance(value, str) or len(value) != 3 or not value.isalpha():
            raise IntegrationRecordTranslationError(
                'ERPNext record has no valid three-letter currency code.'
            )
        return value.upper()

    @staticmethod
    def _status(payload: Mapping[str, Any], doctype: str) -> TransactionStatus:
        """Map an ERPNext document status to the canonical status enum."""
        status = str(payload.get('status', '')).lower()

        if status in {'cancelled', 'canceled'}:
            return TransactionStatus.CANCELLED
        if doctype == 'Payment Entry' or status in {'paid', 'settled', 'completed'}:
            return TransactionStatus.SETTLED
        if status == 'overdue':
            return TransactionStatus.OVERDUE

        return TransactionStatus.PENDING

    @staticmethod
    def _counterparty(
        payload: Mapping[str, Any], doctype: str
    ) -> tuple[str | None, str | None, CounterpartyType | None]:
        """Extract a counterparty identity from an ERPNext record."""
        if doctype == 'Sales Invoice':
            return (
                payload.get('customer'),
                payload.get('customer_name') or payload.get('customer'),
                CounterpartyType.CUSTOMER,
            )
        if doctype == 'Purchase Invoice':
            return (
                payload.get('supplier'),
                payload.get('supplier_name') or payload.get('supplier'),
                CounterpartyType.SUPPLIER,
            )
        party = payload.get('party')
        return party, party, CounterpartyType.OTHER

    @staticmethod
    def _payload_hash(payload: Mapping[str, Any]) -> str:
        """Return a stable hash for the source payload."""
        encoded = json.dumps(payload, sort_keys=True, default=str).encode('utf-8')
        return hashlib.sha256(encoded).hexdigest()
