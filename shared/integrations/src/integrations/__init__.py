"""Shared integrations package."""

from integrations.erpnext import ERPNextAdapter
from integrations.interfaces import IIngestionAdapter
from integrations.models import (
    CanonicalTransactionRecord,
    IngestionAdapterContext,
    RawIngestionRecord,
)
from integrations.registry import IngestionAdapterRegistry

__all__ = [
    'CanonicalTransactionRecord',
    'ERPNextAdapter',
    'IIngestionAdapter',
    'IngestionAdapterContext',
    'IngestionAdapterRegistry',
    'RawIngestionRecord',
]
