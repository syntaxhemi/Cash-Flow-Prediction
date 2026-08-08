from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Enterprise:
    id: UUID
    external_key: str
    legal_name: str
    registration_number: str | None
    industry: str | None
    country_code: str
    base_currency: str
    timezone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
