from typing import Literal
from uuid import UUID

from pydantic import Field, AliasChoices

from app.params.common_query_params import CommonQueryParams


class OrganizationQueryParams(CommonQueryParams):
    active: bool | None = None
    ura_number: str | None = Field(
        alias="identifier",
        validation_alias=AliasChoices("ura_number", "identifier"),
        default=None,
    )
    name: str | None = None
    parent_organization_id: UUID | None = Field(
        alias="partOf",
        validation_alias=AliasChoices("parent_organization_id", "partOf"),
        default=None,
    )
    type: Literal[
        "prov",
        "dept",
        "team",
        "govt",
        "ins",
        "pay",
        "edu",
        "reli",
        "crs",
        "cg",
        "bus",
        "other",
        None,
    ] = None
    include: Literal["Organization.endpoint", None] = Field(
        alias="_include",
        validation_alias=AliasChoices("include", "_include"),
        default=None,
    )
    rev_include: Literal[
        "Location:organization",
        "OrganizationAffiliation:participating-organization",
        "OrganizationAffiliation:primary-organization",
        None,
    ] = Field(
        alias="_revInclude",
        validation_alias=AliasChoices("rev_include", "_revInclude"),
        default=None,
    )
