from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.container import get_matching_care_service
from app.services.matching_care_service import MatchingCareService
from app.params.endpoint_query_params import EndpointQueryParams

router = APIRouter(
    prefix="/Endpoint",
    tags=["Endpoints"],
)


@router.get(
    "",
)
def find_endpoins(
    query_params: EndpointQueryParams = Depends(),
    service: MatchingCareService = Depends(get_matching_care_service),
) -> list[Dict[str, Any]]:
    return service.find_endpoints(query_params)
