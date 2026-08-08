from pydantic import BaseModel
from schemas.ingestion import IngestionSourceCredentialSchema

from api.core.pagination import OffsetPaginationSchema


class IngestionSourceCredentialListResponse(BaseModel):
    """Paginated ingestion-source credential response."""

    items: list[IngestionSourceCredentialSchema]
    pagination: OffsetPaginationSchema
