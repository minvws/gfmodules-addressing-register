from typing import Literal

from pydantic import AliasChoices, Field

from app.params.common_query_params import CommonQueryParams


class OrganizationQueryParams(CommonQueryParams):
    active: bool | None = None
    ura_number: str | None = Field(
        alias="identifier",
        validation_alias=AliasChoices("ura_number", "identifier"),
        default=None,
    )
    name: str | None = None
    parent_organization_id: str | None = Field(
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
    include: Literal["Organization:endpoint", None] = Field(
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
    address: str | None = None
    address_city: str | None = None
    address_country: str | None = None
    address_postal_code: str | None = None
    address_state: str | None = None
    address_use: str | None = None
    phonetic: str | None = None
    endpoint: str | None = None
