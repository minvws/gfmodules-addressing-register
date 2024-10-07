from uuid import UUID

from pydantic import Field
from app.params.common_query_params import CommonQueryParams


class EndpointQueryParams(CommonQueryParams):
    identifier: UUID | None = None
    organization_id: UUID | None = Field(alias="organization", default=None)
