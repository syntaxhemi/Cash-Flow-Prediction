from pydantic import BaseModel
from schemas.ingestion import IngestionRunSchema

from api.core.pagination import OffsetPaginationSchema


class IngestionRunListResponse(BaseModel):
    """Paginated ingestion-run response."""

    items: list[IngestionRunSchema]
    pagination: OffsetPaginationSchema
