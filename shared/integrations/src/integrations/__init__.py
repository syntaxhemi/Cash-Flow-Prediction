"""Shared integrations package."""

from integrations.csv import CSVFileAdapter
from integrations.erpnext import ERPNextAdapter
from integrations.excel import ExcelFileAdapter
from integrations.interfaces import IIngestionAdapter
from integrations.models import (
    CanonicalTransactionRecord,
    IngestionAdapterContext,
    RawIngestionRecord,
)
from integrations.registry import IngestionAdapterRegistry

__all__ = [
    'CSVFileAdapter',
    'CanonicalTransactionRecord',
    'ERPNextAdapter',
    'ExcelFileAdapter',
    'IIngestionAdapter',
    'IngestionAdapterContext',
    'IngestionAdapterRegistry',
    'RawIngestionRecord',
]
