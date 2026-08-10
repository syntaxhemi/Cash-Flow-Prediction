import csv as csv_module
import hashlib
import json
from collections.abc import AsyncIterator
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any

from domain.enterprise import CounterpartyType
from domain.financial import TransactionDirection, TransactionStatus, TransactionType

from integrations.exceptions import (
    IntegrationConfigurationError,
    IntegrationFileError,
    IntegrationRecordTranslationError,
)
from integrations.file_validation import (
    row_payload,
    validate_file_path,
    validate_headers,
)
from integrations.models import (
    CanonicalTransactionRecord,
    IngestionAdapterContext,
    RawIngestionRecord,
)


class CSVFileAdapter:
    """Read canonical accounting transactions from a UTF-8 CSV file."""

    @property
    def source_key(self) -> str:
        """Return the stable CSV source key.

        Returns:
            The registry key for CSV file ingestion.
        """
        return 'csv'

    async def validate_configuration(self, context: IngestionAdapterContext) -> None:
        """Validate the staged CSV file reference and parser configuration.

        Args:
            context: Source and synchronization context.

        Raises:
            IntegrationConfigurationError: If CSV configuration is invalid.

        Returns:
            ``None`` when the configuration is valid.
        """
        if context.file_format != self.source_key:
            raise IntegrationConfigurationError(
                'CSV adapter requires file_format="csv".'
            )
        validate_file_path(context.file_path, self.source_key)

    async def fetch_records(
        self, context: IngestionAdapterContext
    ) -> AsyncIterator[RawIngestionRecord]:
        """Yield raw records from a UTF-8 CSV file.

        Args:
            context: Source and staged-file context.

        Yields:
            One raw record for each non-empty CSV row.

        Raises:
            IntegrationFileError: If the file, headers, encoding, or row shape is
                invalid.
        """
        await self.validate_configuration(context)
        path = validate_file_path(context.file_path, self.source_key)

        try:
            with path.open('r', encoding='utf-8-sig', newline='') as file:
                reader = csv_module.reader(file)
                raw_headers = next(reader, None)

                if raw_headers is None:
                    raise IntegrationFileError('CSV file is empty.')

                headers = validate_headers(raw_headers)

                for row_number, values in enumerate(reader, start=2):
                    if not any(str(value).strip() for value in values):
                        continue
                    if len(values) != len(headers):
                        raise IntegrationFileError(
                            f'Row {row_number} has {len(values)} columns; '
                            f'expected {len(headers)}.'
                        )
                    payload = row_payload(values, headers, row_number=row_number)

                    yield RawIngestionRecord(
                        source_record_id=str(
                            payload.get('source_record_id') or ''
                        ).strip(),
                        payload={**payload, '_row_number': row_number},
                    )

        except UnicodeDecodeError as error:
            raise IntegrationFileError('CSV file must use UTF-8 encoding.') from error

    def translate_record(
        self,
        context: IngestionAdapterContext,
        record: RawIngestionRecord,
    ) -> CanonicalTransactionRecord:
        """Translate one CSV row into a canonical transaction.

        Args:
            context: Source and staged-file context.
            record: Raw CSV row to translate.

        Returns:
            The canonical transaction represented by the row.

        Raises:
            IntegrationRecordTranslationError: If a row value is invalid.
        """
        row_number = int(record.payload.get('_row_number', 0))
        payload = {
            key: value
            for key, value in record.payload.items()
            if not key.startswith('_')
        }
        source_record_id = str(payload.get('source_record_id') or '').strip()
        source_record_id = source_record_id or (
            f'{context.file_sha256 or "csv"}:row:{row_number}'
        )

        try:
            transaction_date = _parse_date(
                payload.get('transaction_date'), 'transaction_date'
            )
            due_date = _parse_optional_date(payload.get('due_date'), 'due_date')
            settlement_date = _parse_optional_date(
                payload.get('settlement_date'), 'settlement_date'
            )

            if due_date is not None and due_date < transaction_date:
                raise ValueError('due_date cannot precede transaction_date')
            if settlement_date is not None and settlement_date < transaction_date:
                raise ValueError('settlement_date cannot precede transaction_date')

            currency_code = _required_text(
                payload.get('currency_code'), 'currency_code'
            ).upper()

            if len(currency_code) != 3 or not currency_code.isalpha():
                raise ValueError('currency_code must be a three-letter code')

            return CanonicalTransactionRecord(
                source_record_id=source_record_id,
                transaction_type=_parse_enum(
                    payload.get('transaction_type'), TransactionType, 'transaction_type'
                ),
                transaction_date=transaction_date,
                due_date=due_date,
                settlement_date=settlement_date,
                amount=_parse_amount(payload.get('amount'), 'amount'),
                currency_code=currency_code,
                direction=_parse_enum(
                    payload.get('direction'), TransactionDirection, 'direction'
                ),
                status=_parse_enum(
                    payload.get('status') or TransactionStatus.PENDING,
                    TransactionStatus,
                    'status',
                ),
                counterparty_external_key=_optional_text(
                    payload.get('counterparty_external_key')
                ),
                counterparty_name=_optional_text(payload.get('counterparty_name')),
                counterparty_type=_parse_optional_enum(
                    payload.get('counterparty_type'),
                    CounterpartyType,
                    'counterparty_type',
                ),
                reference_number=_optional_text(payload.get('reference_number')),
                description=_optional_text(payload.get('description')),
                source_payload_hash=_payload_hash(payload),
            )
        except (TypeError, ValueError, InvalidOperation) as error:
            raise IntegrationRecordTranslationError(
                f'Row {row_number} is invalid: {error}'
            ) from error


def _parse_date(value: object, field_name: str) -> date:
    """Parse a required ISO date value from a CSV row.

    Args:
        value: Raw date value.
        field_name: Field name used in validation errors.

    Returns:
        The parsed date.

    Raises:
        ValueError: If the value is missing or not an ISO date.
    """
    text = _required_text(value, field_name)
    return date.fromisoformat(text[:10])


def _parse_optional_date(value: object, field_name: str) -> date | None:
    """Parse an optional ISO date value from a CSV row.

    Args:
        value: Raw optional date value.
        field_name: Field name used in validation errors.

    Returns:
        The parsed date, or ``None`` for a blank value.
    """
    if value is None or not str(value).strip():
        return None
    return _parse_date(value, field_name)


def _parse_amount(value: object, field_name: str) -> Decimal:
    """Parse a positive decimal amount from a CSV row.

    Args:
        value: Raw amount value.
        field_name: Field name used in validation errors.

    Returns:
        The parsed positive decimal amount.

    Raises:
        ValueError: If the value is missing, invalid, or not positive.
    """
    amount = Decimal(_required_text(value, field_name).replace(',', ''))
    if amount <= 0:
        raise ValueError(f'{field_name} must be positive')
    return amount


def _required_text(value: object, field_name: str) -> str:
    """Return a required non-empty text value from a CSV row.

    Args:
        value: Raw text value.
        field_name: Field name used in validation errors.

    Returns:
        The trimmed text value.

    Raises:
        ValueError: If the value is blank.
    """
    if value is None or not str(value).strip():
        raise ValueError(f'{field_name} is required')
    return str(value).strip()


def _optional_text(value: object) -> str | None:
    """Return a trimmed optional text value from a CSV row.

    Args:
        value: Raw optional text value.

    Returns:
        The trimmed text value, or ``None`` for a blank value.
    """
    if value is None or not str(value).strip():
        return None
    return str(value).strip()


def _parse_enum[EnumT: Enum](
    value: object, enum_type: type[EnumT], field_name: str
) -> EnumT:
    """Parse a case-insensitive domain enum value from a CSV row.

    Args:
        value: Raw enum value.
        enum_type: Domain enum class to instantiate.
        field_name: Field name used in validation errors.

    Returns:
        The parsed enum member.

    Raises:
        ValueError: If the value is missing or unsupported.
    """
    text = _required_text(value, field_name).lower()
    try:
        return enum_type(text)
    except ValueError as error:
        allowed = ', '.join(str(item.value) for item in enum_type)
        raise ValueError(f'{field_name} must be one of: {allowed}') from error


def _parse_optional_enum[EnumT: Enum](
    value: object, enum_type: type[EnumT], field_name: str
) -> EnumT | None:
    """Parse an optional domain enum value from a CSV row.

    Args:
        value: Raw optional enum value.
        enum_type: Domain enum class to instantiate.
        field_name: Field name used in validation errors.

    Returns:
        The parsed enum member, or ``None`` for a blank value.
    """
    if value is None or not str(value).strip():
        return None
    return _parse_enum(value, enum_type, field_name)


def _payload_hash(payload: dict[str, Any]) -> str:
    """Return a stable hash for a normalized CSV row payload.

    Args:
        payload: Normalized row values.

    Returns:
        A SHA-256 hex digest for the payload.
    """
    encoded = json.dumps(payload, sort_keys=True, default=str).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()
