from pydantic import BaseModel
from schemas.enterprise import EnterpriseSchema

from api.core.pagination import OffsetPaginationSchema


class EnterpriseListResponse(BaseModel):
    """Paginated enterprise response."""

    items: list[EnterpriseSchema]
    pagination: OffsetPaginationSchema
