from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file=('.env', '.env.production', '.env.development'),
    )

    ENVIRONMENT: Literal['development', 'testing', 'production'] = 'development'
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_USERNAME: str = 'postgres'
    DB_PASSWORD: SecretStr = SecretStr('postgres')
    DB_NAME: str = 'cash_flow'

    @property
    def DATABASE_URL(self) -> str:
        """Build the async PostgreSQL connection URL."""
        parsed_username = quote_plus(self.DB_USERNAME)
        parsed_password = quote_plus(self.DB_PASSWORD.get_secret_value())

        ssl_param = ''
        if self.ENVIRONMENT == 'production':
            ssl_param = '?sslmode=require'

        return (
            f'postgresql+asyncpg://{parsed_username}:{parsed_password}'
            f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}{ssl_param}'
        )


@lru_cache
def get_database_settings() -> DatabaseSettings:
    """Return cached database settings loaded from the environment."""
    return DatabaseSettings()
