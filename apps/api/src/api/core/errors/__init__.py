"""API error definitions package."""

from api.core.errors.handlers import register_exception_handlers
from api.core.errors.mapping import DomainErrorMapping, get_domain_error_mapping

__all__ = [
    'DomainErrorMapping',
    'get_domain_error_mapping',
    'register_exception_handlers',
]
