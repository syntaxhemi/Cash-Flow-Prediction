from pydantic import Field
from schemas.base import SchemaModel


class OffsetPaginationSchema(SchemaModel):
    """Metadata for offset-based collection responses."""

    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
    total_count: int = Field(ge=0)
    has_next: bool
    has_prev: bool
