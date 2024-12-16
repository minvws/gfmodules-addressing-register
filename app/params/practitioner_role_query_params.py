from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, Field

from app.params.common_query_params import CommonQueryParams


class PractitionerRoleQueryParams(CommonQueryParams):
    active: bool | None = None
    date: datetime | None = Field(
        default=None,
    )
    identifier: str | None = None
    location: str | None = None
    organization: str | None = None
    practitioner: str | None = None
    role: str | None = None
    service: str | None = None
    specialty: str | None = None
    include: Literal["PractitionerRole:practitioner", None] = Field(
        alias="_include",
        validation_alias=AliasChoices("include", "_include"),
        default=None,
    )
