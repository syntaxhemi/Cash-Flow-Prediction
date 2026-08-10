import math
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from integrations.exceptions import IntegrationFileError

REQUIRED_COLUMNS = frozenset(
    {
        'source_record_id',
        'transaction_type',
        'transaction_date',
        'amount',
        'currency_code',
        'direction',
    }
)
OPTIONAL_COLUMNS = frozenset(
    {
        'due_date',
        'settlement_date',
        'status',
        'counterparty_external_key',
        'counterparty_name',
        'counterparty_type',
        'reference_number',
        'description',
    }
)
SUPPORTED_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS


def normalize_header(value: object) -> str:
    """Normalize external header to the canonical column form."""
    text = str(value).strip().lower()
    return '_'.join(text.replace('-', ' ').split())


def validate_headers(headers: Iterable[object]) -> list[str]:
    """Validate and normalize a file header row.

    Args:
        headers: Raw header values in source order.

    Returns:
        Normalized headers in source order.

    Raises:
        IntegrationFileError: If headers are duplicated, unsupported, or incomplete.
    """
    normalized = [normalize_header(header) for header in headers]
    duplicates = sorted(
        {header for header in normalized if header and normalized.count(header) > 1}
    )
    if duplicates:
        raise IntegrationFileError(
            f'The file contains duplicate column headers: {", ".join(duplicates)}.'
        )

    unsupported = sorted(set(normalized) - SUPPORTED_COLUMNS)
    if unsupported:
        raise IntegrationFileError(
            f'The file contains unsupported columns: {", ".join(unsupported)}.'
        )

    missing = sorted(REQUIRED_COLUMNS - set(normalized))
    if missing:
        raise IntegrationFileError(
            f'The file is missing required columns: {", ".join(missing)}.'
        )
    return normalized


def row_payload(
    values: Iterable[object], headers: list[str], *, row_number: int
) -> dict[str, Any]:
    """Build a canonical-keyed row payload from source values.

    Empty headers are ignored when their corresponding value is blank. A value under
    an empty header is rejected because it cannot be mapped safely.

    Args:
        values: Raw values in source order.
        headers: Normalized headers in source order.
        row_number: 1-indexed source row number for error messages.

    Returns:
        Canonical-keyed row values.

    Raises:
        IntegrationFileError: If a value appears under an empty header.
    """
    payload: dict[str, Any] = {}

    for header, value in zip(headers, values, strict=False):
        cleaned_value = _clean_value(value)
        if not header:
            if cleaned_value is not None and str(cleaned_value).strip():
                raise IntegrationFileError(
                    f'Row {row_number} contains a value under an empty column header.'
                )
            continue
        payload[header] = cleaned_value

    return payload


def _clean_value(value: object) -> object:
    """Normalize blank scalar values from text and spreadsheet readers."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, str):
        return value.strip()
    return value


def validate_file_path(context_path: str | None, expected_format: str) -> Path:
    """Validate a staged file path before reading it."""
    if not context_path:
        raise IntegrationFileError('A staged file path is required for file ingestion.')

    path = Path(context_path)
    if not path.is_file():
        raise IntegrationFileError(f'Staged file does not exist: {path.name}.')
    if expected_format not in {'csv', 'excel'}:
        raise IntegrationFileError(f'Unsupported file format: {expected_format}.')

    return path
