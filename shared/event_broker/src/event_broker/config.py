from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class EventBrokerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file=('.env', '.env.production', '.env.development'),
    )

    ENVIRONMENT: Literal['development', 'testing', 'production'] = 'development'
    EVENT_BROKER_HOST: str = 'localhost'
    EVENT_BROKER_PORT: int = 6379
    EVENT_BROKER_DB: int = 0
    EVENT_BROKER_USERNAME: str | None = None
    EVENT_BROKER_PASSWORD: SecretStr | None = None
    EVENT_BROKER_DEFAULT_STREAM_MAXLEN: int | None = 10000

    @property
    def EVENT_BROKER_URL(self) -> str:
        """Build the async Redis URL for the event broker.

        Returns:
            A Redis URL assembled from the configured components.
        """
        scheme = 'rediss' if self.ENVIRONMENT == 'production' else 'redis'
        auth_segment = ''
        if (
            self.EVENT_BROKER_USERNAME is not None
            or self.EVENT_BROKER_PASSWORD is not None
        ):
            username = quote_plus(self.EVENT_BROKER_USERNAME or '')
            password = quote_plus(
                self.EVENT_BROKER_PASSWORD.get_secret_value()
                if self.EVENT_BROKER_PASSWORD
                else ''
            )
            auth_segment = f'{username}:{password}@'

        return (
            f'{scheme}://{auth_segment}{self.EVENT_BROKER_HOST}:'
            f'{self.EVENT_BROKER_PORT}/{self.EVENT_BROKER_DB}'
        )


@lru_cache
def get_event_broker_settings() -> EventBrokerSettings:
    """Return cached event-broker settings loaded from the environment."""
    return EventBrokerSettings()
