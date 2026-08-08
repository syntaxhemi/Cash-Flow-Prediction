from enum import StrEnum


class IngestionSourceStatus(StrEnum):
    ACTIVE = 'active'
    PAUSED = 'paused'
    ERROR = 'error'


class CredentialType(StrEnum):
    API_KEY = 'api_key'
    USERNAME_PASSWORD = 'username_password'
    OAUTH2 = 'oauth2'
    OTHER = 'other'


class CredentialStatus(StrEnum):
    ACTIVE = 'active'
    EXPIRED = 'expired'
    REVOKED = 'revoked'
    ERROR = 'error'


class IngestionRunType(StrEnum):
    FULL = 'full'
    INCREMENTAL = 'incremental'
    UPLOAD = 'upload'


class IngestionStatus(StrEnum):
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
