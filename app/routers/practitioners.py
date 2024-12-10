import logging
from typing import Annotated, Any, Dict
from uuid import UUID

from fastapi import APIRouter, Body, Depends
from fhir.resources.R4B.practitioner import (
    Practitioner as FhirPractitioner,
)
from starlette.responses import Response

from app.container import get_practitioner_service
from app.exceptions.service_exceptions import (
    InvalidResourceException,
    ResourceNotFoundException,
)
from app.mappers.fhir_mapper import (
    BundleType,
    create_bundle_entries,
    create_fhir_bundle,
)
from app.params.history_query_params import HistoryRequest
from app.params.practitioner_query_params import PractitionerQueryParams
from app.routers.utils import FhirBundleResponse, FhirEntityResponse
from app.services.entity_services.practitioner import PractitionerService

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/Practitioner",
    tags=["Practitioner"],
)


@router.post("")
async def create(
    data: Annotated[Dict[str, Any], Body()],
    service: PractitionerService = Depends(get_practitioner_service),
) -> Response:
    fhir_data = FhirPractitioner(**data)
    if fhir_data is None:
        logger.error("Practitioner resource is invalid")
        raise ResourceNotFoundException("Practitioner resource is invalid")

    # Check if the ID is present in the resource
    if fhir_data.id is not None:
        logging.error("Practitioner ID is found in resource")
        raise InvalidResourceException("Practitioner ID is found in resource. Use PUT to update")

    entry = service.add_one(fhir_data)
    return FhirEntityResponse(entry, status_code=201)


@router.get("/_search")
def find(
    query_params: PractitionerQueryParams = Depends(),
    service: PractitionerService = Depends(get_practitioner_service),
) -> Response:
    entries = list(service.find(query_params.model_dump()))

    bundle = create_fhir_bundle(
        bundled_entries=create_bundle_entries(entries, with_req_resp=False),
        bundle_type=BundleType.SEARCHSET,
    ).dict()

    return FhirBundleResponse(bundle)


@router.put("/{_id}")
def update(
    _id: UUID,
    data: Dict[str, Any],
    service: PractitionerService = Depends(get_practitioner_service),
) -> Response:
    fhir_data = FhirPractitioner(**data)
    if fhir_data is None:
        logger.error(f"Practitioner resource is invalid: {_id}")
        raise InvalidResourceException("Practitioner resource is invalid")

    if _id != UUID(fhir_data.id):
        logging.error(f"Practitioner ID not found in resource: {_id}")
        raise InvalidResourceException("Practitioner ID not found in resource")

    entry = service.update_one(_id, fhir_data)
    return FhirEntityResponse(entry)


@router.delete("/{_id}")
def delete(
    _id: UUID,
    service: PractitionerService = Depends(get_practitioner_service),
) -> Response:
    if not service.get_one(_id):
        logger.error(f"Practitioner resource is invalid: {_id}")
        raise ResourceNotFoundException("Practitioner resource is invalid")

    service.delete_one(_id)

    return Response(
        content="",
        status_code=204,
    )


@router.get(
    "/{_id}/_history/{version_id}",
    summary="Find a specific history version for the given resource",
)
def get_history_version(
    _id: UUID,
    version_id: int,
    service: PractitionerService = Depends(get_practitioner_service),
) -> Response:
    entry = service.get_one_version(resource_id=_id, version_id=version_id)
    if entry is None:
        logger.error("Practitioner resource is invalid")
        raise ResourceNotFoundException("Practitioner resource is invalid")

    return FhirEntityResponse(entry)


@router.get(
    "/{_id}/_history",
    summary="Find all versions for the given resource",
)
@router.get(
    "/_history",
    summary="Find all versions for the all resources",
)
def get_history(
    _id: UUID | None = None,
    _since: HistoryRequest = Depends(),
    service: PractitionerService = Depends(get_practitioner_service),
) -> Response:
    if _id is None:
        # Fetch all history entries
        entries = service.find_history(since=_since.since)
    else:
        # Fetch history for specific version
        entries = service.find_history(id=_id, since=_since.since)

    bundle = create_fhir_bundle(
        bundled_entries=create_bundle_entries(entries, with_req_resp=True),
        bundle_type=BundleType.HISTORY,
    ).dict()

    return FhirBundleResponse(bundle)


@router.get("/{_id}")
def get(
    _id: UUID,
    service: PractitionerService = Depends(get_practitioner_service),
) -> Response:
    entry = service.get_one(_id)
    if entry is None:
        logger.error("Practitioner resource is invalid")
        raise ResourceNotFoundException("Practitioner resource is invalid")

    return FhirEntityResponse(entry)
