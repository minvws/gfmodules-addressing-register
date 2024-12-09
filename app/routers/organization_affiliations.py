from typing import Annotated, Any, Dict
from uuid import UUID

from fastapi import APIRouter, Body, Depends
from fastapi.exceptions import HTTPException
from fhir.resources.R4B.organizationaffiliation import OrganizationAffiliation

from app.container import (
    get_organization_affiliation_service,
)
from app.params.organization_affiliation_query_params import (
    OrganizationAffiliationQueryParams,
)
from app.services.organization_affiliation_service import OrganizationAffiliationService

router = APIRouter(
    prefix="/OrganizationAffiliation",
    tags=["Organization Affiliation"],
)


@router.post("")
async def create(
    data: Annotated[Dict[str, Any], Body()],
    service: OrganizationAffiliationService = Depends(
        get_organization_affiliation_service
    ),
) -> Dict[str, Any] | None:
    try:
        params = OrganizationAffiliation(**data)
        return service.add_one(params).data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{_id}")
@router.get("")
def find_organization_affiliates(
    _id: UUID | None = None,
    query_params: OrganizationAffiliationQueryParams = Depends(),
    service: OrganizationAffiliationService = Depends(
        get_organization_affiliation_service
    ),
) -> dict[str, Any]:
    if _id:
        query_params.id = _id
    return service.find_affiliations(query_params)
