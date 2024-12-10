from app.params.common_query_params import CommonQueryParams


class PractitionerQueryParams(CommonQueryParams):
    active: bool | None = None
    identifier: str | None = None
    name: str | None = None
    given: str | None = None
    family: str | None = None
