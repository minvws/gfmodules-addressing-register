
from pydantic import Field
from app.params.common_query_params import CommonQueryParams


class EndpointQueryParams(CommonQueryParams):
    connection_type: str | None = Field(alias='connection-type', default=None)
    identifier: str | None = None
    name: str | None = None
    organization: str | None = Field(alias="organization", default=None)
    payload_type: str | None = Field(alias='payload-type', default=None)
    status: str | None = None
