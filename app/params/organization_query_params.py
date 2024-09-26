from typing import Literal
from uuid import UUID


from app.params.common_query_params import CommonQueryParams


class OrganizationQueryParams(CommonQueryParams):
    active: bool | None = None
    identifier: str | None = None
    name: str | None | None = None
    partOf: UUID | None = None
    type: str | None = None  # possible enum
    include: Literal["Organization.endpoint", None] = None
    revInclude: Literal[
        "Location:organization",
        "OrganizationAffiliation:participating-organization",
        "OrganizationAffiliation:primary-organization",
        None,
    ] = None
