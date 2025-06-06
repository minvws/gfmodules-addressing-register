from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, Field

from app.params.common_query_params import CommonQueryParams


class OrganizationAffiliationQueryParams(CommonQueryParams):
    active: bool | None = None
    date: datetime | None = Field(
        default=None,
    )
    identifier: str | None = None
    name: str | None = None
    participating_organization: str | None = None
    primary_organization: str | None = None
    specialty: Literal["Radiology", None] = None
    role: Literal[
        "BM",
        "provider",
        "agency",
        "research",
        "payer",
        "diagnostics",
        "supplier",
        "HIE/HIO",
        "member",
        None,
    ] = None
    include: Literal["OrganizationAffiliation.endpoint", None] = Field(
        alias="_include",
        validation_alias=AliasChoices("include", "_include"),
        default=None,
    )
