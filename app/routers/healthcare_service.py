import logging
from uuid import UUID
from typing import Any, Dict

from fastapi import APIRouter, Depends
from fhir.resources.R4B.healthcareservice import HealthcareService as FhirHealthcareService
from starlette.responses import Response

from app.container import get_healthcare_service_service
from app.params.healthcare_service_query_params import HealthcareServiceQueryParams
from app.services.entity_services.healthcare_service_service import HealthcareServiceService
from app.exceptions.service_exceptions import InvalidResourceException
from app.mappers.fhir_mapper import create_fhir_bundle, BundleType, create_bundle_entries
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.routers.utils import FhirEntityResponse, FhirBundleResponse

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/HealthcareService",
    tags=["Healthcare Service"],
)

@router.post("")
def create(
    data: Dict[str, Any],
    service: HealthcareServiceService = Depends(get_healthcare_service_service),
) -> Response:
    fhir_data = FhirHealthcareService(**data)
    if fhir_data is None:
        logger.error("Healthcare Service resource is invalid")
        raise ResourceNotFoundException("Healthcare Service resource is invalid")

    # Check if the ID is present in the resource
    if fhir_data.id is not None:
        logging.error("Healthcare Service ID is found in healthcare service resource")
        raise InvalidResourceException(
            "Healthcare Service ID is found in healthcare service resource. Use PUT to update"
        )

    entry = service.add_one(fhir_data)
    return FhirEntityResponse(entry, status_code=201)

@router.get("/_search")
def find(
    query_params: HealthcareServiceQueryParams = Depends(),
    service: HealthcareServiceService = Depends(get_healthcare_service_service),
) -> Response:
    entries = service.find(query_params.model_dump())

    bundle = create_fhir_bundle(
        bundled_entries=create_bundle_entries(entries, with_req_resp=False),
        bundle_type=BundleType.SEARCHSET,
    ).dict()

    return FhirBundleResponse(bundle)


@router.put("/{_id}")
def update(
    _id: UUID,
    data: Dict[str, Any],
    service: HealthcareServiceService = Depends(get_healthcare_service_service),
) -> Response:
    fhir_data = FhirHealthcareService(**data)
    if fhir_data is None:
        logger.error(f"Healthcare Service resource is invalid: {_id}")
        raise ResourceNotFoundException("Healthcare Service resource is invalid")

    if _id != UUID(fhir_data.id):
        logging.error(f"Healthcare Service ID not found in healthcare service resource: {_id}")
        raise InvalidResourceException(
            "Healthcare Service ID not found in healthcare service resource"
        )

    entry = service.update_one(_id, fhir_data)
    return FhirEntityResponse(entry)


@router.delete("/{_id}")
def delete(
    _id: UUID,
    service: HealthcareServiceService = Depends(get_healthcare_service_service),
) -> Response:
    if not service.get_one(_id):
        logger.error(f"Healthcare Service resource is invalid: {_id}")
        raise ResourceNotFoundException("Healthcare Service resource is invalid")

    service.delete_one(_id)

    return Response(
        content="",
        status_code=204,
    )


@router.get("/{_id}/_history/{version_id}",
    summary="Find a specific history version for the given resource",
)
def get_history_version(
    _id: UUID,
    version_id: int,
    service: HealthcareServiceService = Depends(get_healthcare_service_service),
) -> Response:
    entry = service.get_one_version(resource_id=_id, version_id=version_id)
    if entry is None:
        logger.error("Healthcare Service resource is invalid")
        raise ResourceNotFoundException("Healthcare Service resource is invalid")

    return FhirEntityResponse(entry)

@router.get("/{_id}/_history",
    summary="Find all versions for the given resource",
)
@router.get("/_history",
    summary="Find all versions for the all resources",
)
def get_history(
    _id: UUID|None = None,
    service: HealthcareServiceService = Depends(get_healthcare_service_service),
) -> Response:
    if _id is None:
        # Fetch all history entries
        entries = service.find_history()
    else:
        # Fetch history for specific version
        entries = service.find_history(id=_id)

    bundle = create_fhir_bundle(
        bundled_entries=create_bundle_entries(entries, with_req_resp=True),
        bundle_type=BundleType.HISTORY,
    ).dict()

    return FhirBundleResponse(bundle)


@router.get("/{_id}")
def get(
    _id: UUID,
    service: HealthcareServiceService = Depends(get_healthcare_service_service),
) -> Response:
    entry = service.get_one(_id)
    if entry is None:
        logger.error("Healthcare Service resource is invalid")
        raise ResourceNotFoundException("Healthcare Service resource is invalid")

    return FhirEntityResponse(entry)
