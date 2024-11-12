from typing import Any, Annotated, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, Body
from fastapi.exceptions import HTTPException
from fhir.resources.R4B.healthcareservice import HealthcareService

from app.container import get_healthcare_service_service
from app.params.healthcare_service_query_params import HealthcareServiceQueryParams
from app.services.healthcare_service_service import HealthcareServiceService

router = APIRouter(
    prefix="/HealthcareService",
    tags=["Healthcare Service"],
)

@router.post("")
async def create(
    data: Annotated[Dict[str, Any], Body()],
    service: HealthcareServiceService = Depends(get_healthcare_service_service),
) -> Dict[str, Any]:
    try:
        params = HealthcareService(**data)
        return service.add_one(params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{_id}")
@router.get("")
def find(
    _id: UUID | None = None,
    query_params: HealthcareServiceQueryParams = Depends(),
    service: HealthcareServiceService = Depends(get_healthcare_service_service),
) -> dict[str, Any]:
    if _id:
        query_params.id = _id
    return service.find(query_params)
