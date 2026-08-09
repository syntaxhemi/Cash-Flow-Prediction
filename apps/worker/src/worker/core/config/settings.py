from functools import lru_cache
from typing import Literal

from database.config import DatabaseSettings
from event_broker.config import EventBrokerSettings
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    """Settings required by the background worker process."""

    model_config = SettingsConfigDict(
        extra='ignore',
        env_file=('.env', '.env.production', '.env.development'),
    )

    ENVIRONMENT: Literal['development', 'testing', 'production'] = 'development'
    WORKER_LOG_LEVEL: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = 'INFO'
    WORKER_CONSUMER_GROUP: str = 'cash_flow_ingestion_workers'
    WORKER_CONSUMER_NAME: str = 'worker_1'
    WORKER_BATCH_SIZE: int = 10
    WORKER_BLOCK_MS: int = 5000
    INGESTION_SYNC_STREAM_NAME: str = 'cash_flow_ingestion_sync'
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_USERNAME: str = 'postgres'
    DB_PASSWORD: SecretStr = SecretStr('postgres')
    DB_NAME: str = 'cash_flow'
    EVENT_BROKER_HOST: str = 'localhost'
    EVENT_BROKER_PORT: int = 6379
    EVENT_BROKER_DB: int = 0

    @property
    def database_settings(self) -> DatabaseSettings:
        """Return database settings derived from worker configuration."""
        return DatabaseSettings(
            ENVIRONMENT=self.ENVIRONMENT,
            DB_HOST=self.DB_HOST,
            DB_PORT=self.DB_PORT,
            DB_USERNAME=self.DB_USERNAME,
            DB_PASSWORD=self.DB_PASSWORD,
            DB_NAME=self.DB_NAME,
        )

    @property
    def event_broker_settings(self) -> EventBrokerSettings:
        """Return event-broker settings derived from worker configuration."""
        return EventBrokerSettings(
            EVENT_BROKER_HOST=self.EVENT_BROKER_HOST,
            EVENT_BROKER_PORT=self.EVENT_BROKER_PORT,
            EVENT_BROKER_DB=self.EVENT_BROKER_DB,
        )


@lru_cache
def get_worker_settings() -> WorkerSettings:
    """Return cached worker settings loaded from the environment."""
    return WorkerSettings()
