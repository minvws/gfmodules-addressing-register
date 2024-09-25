from uuid import UUID
from app.params.common_query_params import CommonQueryParams


class EndpointQueryParams(CommonQueryParams):
    identifier: str | None = None
    organization: UUID | None = None
