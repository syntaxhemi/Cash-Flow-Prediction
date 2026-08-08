"""Shared database package."""

from database.base import Base, metadata
from database.config import DatabaseSettings, get_database_settings
from database.interfaces import IDatabaseManager, ISessionManager
from database.manager import DatabaseManager
from database.session import (
    AsyncDatabaseConfig,
    SessionManager,
    create_database_engine,
    create_session_factory,
    normalize_async_database_url,
)

__all__ = [
    'AsyncDatabaseConfig',
    'Base',
    'DatabaseManager',
    'DatabaseSettings',
    'IDatabaseManager',
    'ISessionManager',
    'SessionManager',
    'create_database_engine',
    'create_session_factory',
    'get_database_settings',
    'metadata',
    'models',
    'normalize_async_database_url',
]

from database import models
