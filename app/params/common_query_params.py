from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, AliasChoices


class CommonQueryParams(BaseModel):
    id: UUID | None = Field(
        alias="_id", validation_alias=AliasChoices("id", "_id"), default=None
    )
    updated_at: datetime | None = Field(
        alias="_lastUpdated",
        default=None,
        validation_alias=AliasChoices("updated_at", "_lastUpdated"),
    )
