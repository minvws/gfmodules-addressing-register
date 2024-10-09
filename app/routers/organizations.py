from typing import Any

from fastapi import APIRouter, Depends

from app.container import get_matching_care_service
from app.services.matching_care_service import MatchingCareService
from app.params.organization_query_params import OrganizationQueryParams

router = APIRouter(
    prefix="/Organization",
    tags=["Organization"],
)


@router.get("")
def find_organization(
    query_params: OrganizationQueryParams = Depends(),
    service: MatchingCareService = Depends(get_matching_care_service),
) -> dict[str, Any]:
    return service.find_organizations(query_params)
