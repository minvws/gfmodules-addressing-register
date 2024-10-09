from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends

from app.container import get_matching_care_service
from app.services.matching_care_service import MatchingCareService
from app.params.endpoint_query_params import EndpointQueryParams

router = APIRouter(
    prefix="/Endpoint",
    tags=["Endpoints"],
)


@router.get("/{_id}")
@router.get(
    "",
)
def find_endpoints(
    _id: UUID | None = None,
    query_params: EndpointQueryParams = Depends(),
    service: MatchingCareService = Depends(get_matching_care_service),
) -> dict[str, Any]:
    if _id:
        query_params.id = _id
    return service.find_endpoints(query_params)
