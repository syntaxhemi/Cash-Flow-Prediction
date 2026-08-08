from enum import Enum

from sqlalchemy import Enum as SQLEnum


def enum_type(enum_cls: type[Enum], *, name: str) -> SQLEnum:
    return SQLEnum(
        enum_cls,
        name=name,
        values_callable=lambda values: [item.value for item in values],
    )
