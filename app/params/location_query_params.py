from typing import Literal

from pydantic import AliasChoices, Field

from app.params.common_query_params import CommonQueryParams


class LocationQueryParams(CommonQueryParams):
    name: str | None = None
    managing_organization: str | None = None
    part_of: str | None = None
    status: str | None = None
    type: str | None = None
    include: Literal["Location:organization", None] = Field(
        alias="_include",
        validation_alias=AliasChoices("include", "_include"),
        default=None,
    )
