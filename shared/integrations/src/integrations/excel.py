import hashlib
import json
from collections.abc import AsyncIterator
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any

import pandas as pd
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


class ExcelFileAdapter:
    """Read canonical accounting transactions from an Excel workbook."""

    @property
    def source_key(self) -> str:
        """Return the stable Excel source key.

        Returns:
            The registry key for Excel file ingestion.
        """
        return 'excel'

    async def validate_configuration(self, context: IngestionAdapterContext) -> None:
        """Validate the staged Excel workbook reference and parser configuration.

        Args:
            context: Source and synchronization context.

        Raises:
            IntegrationConfigurationError: If Excel configuration is invalid.

        Returns:
            ``None`` when the configuration is valid.
        """
        if context.file_format != self.source_key:
            raise IntegrationConfigurationError(
                'Excel adapter requires file_format="excel".'
            )
        path = validate_file_path(context.file_path, self.source_key)
        if path.suffix.lower() != '.xlsx':
            raise IntegrationConfigurationError(
                'Excel ingestion supports .xlsx files only.'
            )

    async def fetch_records(
        self, context: IngestionAdapterContext
    ) -> AsyncIterator[RawIngestionRecord]:
        """Yield raw records from the selected Excel worksheet.

        Args:
            context: Source and staged-workbook context.

        Yields:
            One raw record for each non-empty worksheet row.

        Raises:
            IntegrationFileError: If the workbook, worksheet, headers, or row shape
                is invalid.
        """
        await self.validate_configuration(context)
        path = validate_file_path(context.file_path, self.source_key)

        try:
            frame = pd.read_excel(
                path,
                sheet_name=context.sheet_name or 0,
                header=0,
                dtype=object,
                engine='openpyxl',
            )

        except (ImportError, OSError, ValueError) as error:
            raise IntegrationFileError(
                f'Excel workbook could not be read: {path.name}.'
            ) from error

        headers = validate_headers(frame.columns.tolist())

        for row_number, values in enumerate(
            frame.itertuples(index=False, name=None), start=2
        ):
            if not any(value is not None and str(value).strip() for value in values):
                continue
            if len(values) != len(headers):
                raise IntegrationFileError(
                    f'Row {row_number} has {len(values)} columns; '
                    f'expected {len(headers)}.'
                )
            payload = row_payload(values, headers, row_number=row_number)

            yield RawIngestionRecord(
                source_record_id=str(payload.get('source_record_id') or '').strip(),
                payload={**payload, '_row_number': row_number},
            )

    def translate_record(
        self,
        context: IngestionAdapterContext,
        record: RawIngestionRecord,
    ) -> CanonicalTransactionRecord:
        """Translate one Excel row into a canonical transaction.

        Args:
            context: Source and staged-workbook context.
            record: Raw Excel row to translate.

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
            f'{context.file_sha256 or "excel"}:row:{row_number}'
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
    """Parse a required date value from an Excel row.

    Args:
        value: Raw date or spreadsheet datetime value.
        field_name: Field name used in validation errors.

    Returns:
        The parsed date.

    Raises:
        ValueError: If the value is missing or invalid.
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(_required_text(value, field_name)[:10])


def _parse_optional_date(value: object, field_name: str) -> date | None:
    """Parse an optional date value from an Excel row.

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
    """Parse a positive decimal amount from an Excel row.

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
    """Return a required non-empty text value from an Excel row.

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
    """Return a trimmed optional text value from an Excel row.

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
    """Parse a case-insensitive domain enum value from an Excel row.

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
    """Parse an optional domain enum value from an Excel row.

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
    """Return a stable hash for a normalized Excel row payload.

    Args:
        payload: Normalized row values.

    Returns:
        A SHA-256 hex digest for the payload.
    """
    encoded = json.dumps(payload, sort_keys=True, default=str).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()
