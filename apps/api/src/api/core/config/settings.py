from functools import lru_cache
from typing import Literal

from database import DatabaseSettings
from event_broker import EventBrokerSettings
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore', env_file=('.env', '.env.development', '.env.production')
    )

    ENVIRONMENT: Literal['development', 'testing', 'production'] = 'development'
    API_TITLE: str = 'Cash Flow Prediction API'
    API_HOST: str = '127.0.0.1'
    API_PORT: int = 8000
    API_LOG_LEVEL: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = 'INFO'
    API_CORS_ALLOW_ORIGINS: list[str] = ['http://localhost:5173']
    API_CORS_ALLOW_CREDENTIALS: bool = True
    API_CORS_ALLOW_METHODS: list[str] = ['*']
    API_CORS_ALLOW_HEADERS: list[str] = ['*']
    INGESTION_SYNC_STREAM_NAME: str = 'cash_flow_ingestion_sync'

    @field_validator(
        'API_CORS_ALLOW_ORIGINS',
        'API_CORS_ALLOW_METHODS',
        'API_CORS_ALLOW_HEADERS',
        mode='before',
    )
    @classmethod
    def parse_csv_list(cls, value: object) -> object:
        """Convert comma-separated environment values into lists.

        Args:
            value: Raw settings value.

        Returns:
            Parsed list for comma-separated text, otherwise the original value.
        """
        if not isinstance(value, str):
            return value
        return [item.strip() for item in value.split(',') if item.strip()]

    @property
    def database_settings(self) -> DatabaseSettings:
        """Return database settings configured for the API environment."""
        return DatabaseSettings(ENVIRONMENT=self.ENVIRONMENT)

    @property
    def event_broker_settings(self) -> EventBrokerSettings:
        """Return event-broker settings configured for the API environment."""
        return EventBrokerSettings(ENVIRONMENT=self.ENVIRONMENT)


@lru_cache
def get_api_settings() -> ApiSettings:
    """Return cached API settings loaded from the environment."""
    return ApiSettings()
