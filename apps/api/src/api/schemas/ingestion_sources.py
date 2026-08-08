from pydantic import BaseModel
from schemas.ingestion import IngestionSourceSchema

from api.core.pagination import OffsetPaginationSchema


class IngestionSourceListResponse(BaseModel):
    """Paginated ingestion-source response."""

    items: list[IngestionSourceSchema]
    pagination: OffsetPaginationSchema
