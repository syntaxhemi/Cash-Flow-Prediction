from dataclasses import dataclass

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from database.config import DatabaseSettings

DEFAULT_POSTGRES_DRIVER = 'postgresql+asyncpg'


@dataclass(slots=True)
class AsyncDatabaseConfig:
    url: str
    echo: bool = False
    pool_pre_ping: bool = True
    pool_size: int = 10
    max_overflow: int = 10

    @classmethod
    def from_settings(cls, settings: DatabaseSettings) -> 'AsyncDatabaseConfig':
        """Create engine configuration from database settings.

        Args:
            settings: Database connection settings.

        Returns:
            Async engine configuration.
        """
        return cls(
            url=settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=10,
        )


def normalize_async_database_url(url: str) -> str:
    """Ensure a PostgreSQL URL uses the asyncpg driver.

    Args:
        url: Database URL to normalize.

    Returns:
        URL with an async PostgreSQL driver when applicable.
    """
    parsed_url = make_url(url)
    drivername = parsed_url.drivername

    if '+' not in drivername and drivername == 'postgresql':
        return str(parsed_url.set(drivername=DEFAULT_POSTGRES_DRIVER))

    return url


def create_database_engine(config: AsyncDatabaseConfig) -> AsyncEngine:
    """Create an async SQLAlchemy engine.

    Args:
        config: Engine connection and pool configuration.

    Returns:
        Configured async engine.
    """
    return create_async_engine(
        normalize_async_database_url(config.url),
        echo=config.echo,
        pool_pre_ping=config.pool_pre_ping,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
    )
