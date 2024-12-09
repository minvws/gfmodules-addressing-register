from app.params.common_query_params import CommonQueryParams


class HealthcareServiceQueryParams(CommonQueryParams):
    active: bool | None = None
    identifier: str | None = None
    location: str | None = None
    name: str | None = None
    organization: str | None = None
    service_type: str | None = None
