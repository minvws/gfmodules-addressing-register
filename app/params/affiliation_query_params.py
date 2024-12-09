from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.params.common_query_params import CommonQueryParams


class OrganizationAffliliationQueryParams(CommonQueryParams, BaseModel):
    active: bool | None = None
    date: datetime | None = None
    participating_organization: UUID | None = None
    primary_organization: UUID | None = None
    role: str | None = None
    include: Literal["OrganizationAffiliation.endpoint", None] = None
