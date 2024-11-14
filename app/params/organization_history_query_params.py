from datetime import datetime

from pydantic import AliasChoices, Field

from app.params.common_query_params import CommonQueryParams



class OrganizationHistoryRequest(CommonQueryParams):
    active: bool | None = None
    endpoint: str | None = Field(
        alias="endpoint",
        validation_alias=AliasChoices("endpoint", "endpoint"),
        default=None,
    )
    identifier: str | None = None
    name: str | None = None
    part_of: str | None = Field(
        alias="part-of",
        validation_alias=AliasChoices("part_of", "part-of"),
        default=None,
    )
    since: datetime | None = Field(
        alias="_since",
        validation_alias=AliasChoices("since", "_since"),
        default=None,
    )
