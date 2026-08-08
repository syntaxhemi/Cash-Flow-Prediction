from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, field_validator

from schemas.base import SchemaModel


class EnterpriseSchema(SchemaModel):
    id: UUID
    external_key: str = Field(min_length=1)
    legal_name: str = Field(min_length=1)
    registration_number: str | None = None
    industry: str | None = None
    country_code: str = Field(min_length=3, max_length=3, pattern=r'^[A-Z]{3}$')
    base_currency: str = Field(min_length=3, max_length=3, pattern=r'^[A-Z]{3}$')
    timezone: str = Field(min_length=1)
    is_active: bool
    created_at: datetime
    updated_at: datetime


class EnterpriseCreateSchema(SchemaModel):
    external_key: str = Field(min_length=1)
    legal_name: str = Field(min_length=1)
    registration_number: str | None = None
    industry: str | None = None
    country_code: str = Field(min_length=3, max_length=3)
    base_currency: str = Field(min_length=3, max_length=3)
    timezone: str = Field(min_length=1)
    is_active: bool = True

    @field_validator('country_code', 'base_currency')
    @classmethod
    def validate_code(cls, value: str) -> str:
        """Normalize and validate a three-letter regional code."""
        value = value.upper()
        if not value.isalpha() or len(value) != 3:
            raise ValueError('Code must contain exactly three letters.')
        return value

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        """Validate that the timezone is available in the system database."""
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as error:
            raise ValueError('Unsupported timezone value.') from error
        return value


class EnterpriseUpdateSchema(SchemaModel):
    legal_name: str | None = Field(default=None, min_length=1)
    registration_number: str | None = None
    industry: str | None = None
    country_code: str | None = Field(default=None, min_length=3, max_length=3)
    base_currency: str | None = Field(default=None, min_length=3, max_length=3)
    timezone: str | None = Field(default=None, min_length=1)
    is_active: bool | None = None

    @field_validator('country_code', 'base_currency')
    @classmethod
    def validate_optional_code(cls, value: str | None) -> str | None:
        """Normalize and validate an optional three-letter code."""
        if value is None:
            return None
        value = value.upper()
        if not value.isalpha() or len(value) != 3:
            raise ValueError('Code must contain exactly three letters.')
        return value

    @field_validator('timezone')
    @classmethod
    def validate_optional_timezone(cls, value: str | None) -> str | None:
        """Validate an optional timezone when a value is supplied."""
        if value is None:
            return None
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as error:
            raise ValueError('Unsupported timezone value.') from error
        return value


class EnterpriseFilterParams(SchemaModel):
    external_key: str | None = Field(default=None, min_length=1)
    legal_name: str | None = Field(default=None, min_length=1)
    is_active: bool = True
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
