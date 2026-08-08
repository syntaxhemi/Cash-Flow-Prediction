"""Base configuration for shared Pydantic schemas."""

from pydantic import BaseModel, ConfigDict


class SchemaModel(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=False,
    )
