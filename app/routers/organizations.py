import logging
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends
from fhir.resources.R4B.organization import Organization as FhirOrganization

from app.container import get_organization_service, get_matching_care_service
from app.exceptions.service_exceptions import InvalidResourceException
from app.params.organization_query_params import OrganizationQueryParams

from app.services.entity_services.organization_service import OrganizationService
from app.services.matching_care_service import MatchingCareService


router = APIRouter(
    prefix="/Organization",
    tags=["Organization"],
)


@router.post("")
def create_organization(
    data: Dict[str, Any],
    service: OrganizationService = Depends(get_organization_service),
) -> dict[str, Any] | None:
    fhir_data = FhirOrganization(**data)
    if fhir_data.id is not None:
        logging.error("Organization ID cannot be in the resource")
        raise InvalidResourceException(
            "Organization ID cannot be in the organization resource"
        )

    return service.add_one(fhir_data).data


@router.get("/_search/{_id}")
@router.get(
    "/_search",
)
def find_organization(
    _id: UUID | None = None,
    query_params: OrganizationQueryParams = Depends(),
    service: MatchingCareService = Depends(get_matching_care_service),
) -> dict[str, Any]:
    if _id:
        query_params.id = _id
    bundle = service.find_organizations(query_params)
    return bundle.dict()  # type:ignore


@router.put("/{_id}")
def update_organization(
    _id: UUID,
    data: Dict[str, Any],
    service: OrganizationService = Depends(get_organization_service),
) -> dict[str, Any] | None:
    fhir_data = FhirOrganization(**data)
    if fhir_data.id is None:
        logging.error("Organization ID not found in organization resource")
        raise InvalidResourceException(
            "Organization ID not found in organization resource"
        )

    if _id != UUID(fhir_data.id):
        logging.error("Organization ID in the resource does not match the URL")
        raise InvalidResourceException(
            f"Organization ID {str(fhir_data.id)} in the resource does not match the URL {str(_id)}"
        )

    return service.update_one(_id, fhir_data).data


@router.delete("/{_id}")
def delete_organization(
    _id: UUID,
    service: OrganizationService = Depends(get_organization_service),
) -> None:
    return service.delete_one(_id)


@router.get("/{_id}/_history/{version_id}")
def get_organization_version(
    _id: UUID,
    version_id: int,
    service: OrganizationService = Depends(get_organization_service),
) -> Dict[str, Any]:
    results = service.get_one_version(resource_id=_id, version_id=version_id)
    return results.data if results.data is not None else results.bundle_meta


@router.get("/{_id}/_history")
@router.get("/_history")
def find_organization_history(
    _id: UUID | None = None,
    service: MatchingCareService = Depends(get_matching_care_service),
) -> dict[str, Any]:
    return service.find_organizations_history(organization_id=_id)


@router.get("/{_id}")
def get_organization(
    _id: UUID,
    service: OrganizationService = Depends(get_organization_service),
) -> Dict[str, Any] | None:
    org = service.get_one(_id)
    return org.data
