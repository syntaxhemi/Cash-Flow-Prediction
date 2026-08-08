from uuid import UUID

from database import IUnitOfWork
from domain.enterprise.rules import DefaultEnterpriseRules
from schemas.enterprise import (
    EnterpriseCreateSchema,
    EnterpriseFilterParams,
    EnterpriseSchema,
    EnterpriseUpdateSchema,
)

from api.core.pagination import OffsetPaginationSchema
from api.schemas.enterprise import EnterpriseListResponse


class EnterpriseService:
    def __init__(self, uow: IUnitOfWork) -> None:
        """Initialize enterprise application operations.

        Args:
            uow: Unit of work used for persistence.
        """
        self._uow = uow
        self._rules = DefaultEnterpriseRules()

    async def create(self, payload: EnterpriseCreateSchema) -> EnterpriseSchema:
        """Validate and create an enterprise.

        Args:
            payload: Enterprise creation data.

        Returns:
            The created enterprise schema.
        """
        self._rules.validate_configuration(
            country_code=payload.country_code,
            base_currency=payload.base_currency,
            timezone=payload.timezone,
        )
        model = await self._uow.enterprises.create(payload)
        await self._uow.commit()
        return EnterpriseSchema.model_validate(model)

    async def get(self, enterprise_id: UUID) -> EnterpriseSchema:
        """Return an enterprise by identifier.

        Args:
            enterprise_id: Enterprise identifier to retrieve.

        Returns:
            The enterprise response schema.
        """
        model = await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)
        return EnterpriseSchema.model_validate(model)

    async def list(self, filters: EnterpriseFilterParams) -> EnterpriseListResponse:
        """List enterprises matching the supplied filters.

        Args:
            filters: Enterprise list filters.

        Returns:
            Paginated enterprise response.
        """
        result = await self._uow.enterprises.list(filters)
        items = [EnterpriseSchema.model_validate(model) for model in result.items]
        return EnterpriseListResponse(
            items=items,
            pagination=OffsetPaginationSchema(
                limit=filters.limit,
                offset=filters.offset,
                total_count=result.total_count,
                has_next=filters.offset + len(items) < result.total_count,
                has_prev=filters.offset > 0,
            ),
        )

    async def update(
        self, enterprise_id: UUID, payload: EnterpriseUpdateSchema
    ) -> EnterpriseSchema:
        """Validate and update an enterprise.

        Args:
            enterprise_id: Enterprise identifier to update.
            payload: Enterprise fields to change.

        Returns:
            The updated enterprise schema.
        """
        values = payload.model_dump(exclude_unset=True)
        current = await self._uow.enterprises.get_active_by_id_or_raise(enterprise_id)
        self._rules.validate_configuration(
            country_code=values.get('country_code', current.country_code),
            base_currency=values.get('base_currency', current.base_currency),
            timezone=values.get('timezone', current.timezone),
        )
        model = await self._uow.enterprises.update(enterprise_id, payload)

        await self._uow.commit()
        return EnterpriseSchema.model_validate(model)

    async def delete(self, enterprise_id: UUID) -> None:
        """Soft-delete an enterprise by deactivating it.

        Args:
            enterprise_id: Enterprise identifier to deactivate.

        Raises:
            EnterpriseNotFoundError: If no active enterprise exists.
        """
        await self._uow.enterprises.update(
            enterprise_id,
            EnterpriseUpdateSchema(is_active=False),
        )
        await self._uow.commit()
