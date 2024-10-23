from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends

from app.container import get_matching_care_service
from app.params.organization_history_query_params import OrganizationHistoryRequest
from app.params.organization_query_params import OrganizationQueryParams
from app.services.matching_care_service import MatchingCareService

router = APIRouter(
    prefix="/Organization",
    tags=["Organization"],
)


@router.get("/{_id}/_history")
@router.get("/_history")
def find_organization_history(
    _id: UUID | None = None,
    query_params: OrganizationHistoryRequest = Depends(),
    service: MatchingCareService = Depends(get_matching_care_service),
) -> dict[str, Any]:
    if _id:
        query_params.id = _id
    return service.find_organizations_history(query_params)


@router.get("/{_id}")
@router.get("")
def find_organization(
    _id: UUID | None = None,
    query_params: OrganizationQueryParams = Depends(),
    service: MatchingCareService = Depends(get_matching_care_service),
) -> dict[str, Any]:
    if _id:
        query_params.id = _id
    return service.find_organizations(query_params)
