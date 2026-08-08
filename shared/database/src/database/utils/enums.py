from enum import Enum

from sqlalchemy import Enum as SQLEnum


def enum_type(enum_cls: type[Enum], *, name: str) -> SQLEnum:
    """Create a PostgreSQL enum type from a domain enum.

    Args:
        enum_cls: Domain enum class to persist.
        name: Database enum type name.

    Returns:
        SQLAlchemy enum column type.
    """
    return SQLEnum(
        enum_cls,
        name=name,
        values_callable=lambda values: [item.value for item in values],
    )
