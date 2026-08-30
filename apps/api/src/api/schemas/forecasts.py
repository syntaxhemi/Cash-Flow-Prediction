from schemas.base import SchemaModel
from schemas.forecasting import ForecastRunSchema

from api.core.pagination import OffsetPaginationSchema


class ForecastListResponse(SchemaModel):
    """Paginated forecast-run response."""

    items: list[ForecastRunSchema]
    pagination: OffsetPaginationSchema
