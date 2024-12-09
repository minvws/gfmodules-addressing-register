import logging
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends
from fhir.resources.R4B.endpoint import Endpoint as FhirEndpoint

from app.container import get_endpoint_service, get_matching_care_service
from app.exceptions.service_exceptions import InvalidResourceException
from app.params.endpoint_query_params import EndpointQueryParams
from app.params.history_query_params import HistoryRequest
from app.services.entity_services.endpoint_service import EndpointService
from app.services.matching_care_service import MatchingCareService

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/Endpoint",
    tags=["Endpoints"],
)


@router.post("")
def create(data: Dict[str, Any], service: EndpointService = Depends(get_endpoint_service)) -> Dict[str, Any] | None:
    fhir_data = FhirEndpoint(**data)
    if fhir_data.id is not None:
        logging.error("Endpoint ID cannot be in the resource")
        raise InvalidResourceException("Endpoint ID cannot be in the organization resource")
    new_endpoint = service.add_one(fhir_data)
    return new_endpoint.data


@router.get("/_search/{_id}")
@router.get(
    "/_search",
)
def find_endpoints(
    _id: UUID | None = None,
    query_params: EndpointQueryParams = Depends(),
    service: MatchingCareService = Depends(get_matching_care_service),
) -> Dict[str, Any]:
    if _id:
        query_params.id = _id
    bundle = service.find_endpoints(query_params)
    return bundle.dict()  # type:ignore


@router.put("/{_id}")
def update_endpoint(
    _id: UUID,
    data: Dict[str, Any],
    service: EndpointService = Depends(get_endpoint_service),
) -> Dict[str, Any] | None:
    fhir_data = FhirEndpoint(**data)
    if fhir_data.id is None:
        logging.error("Endpoint ID not found in endpoint resource")
        raise InvalidResourceException("Endpoint ID not found in endpoint resource")

    if _id != UUID(fhir_data.id):
        logging.error("Endpoint ID in the resource does not match the URL")
        raise InvalidResourceException(
            f"Endpoint ID {str(fhir_data.id)} in the resource does not match the URL {str(_id)}"
        )
    return service.update_one(_id, fhir_data).data


@router.delete("/{_id}")
def delete_endpoint(
    _id: UUID,
    service: EndpointService = Depends(get_endpoint_service),
) -> None:
    return service.delete_one(_id)


@router.get("/{_id}/_history/{version_id}")
def get_endpoint_version(
    _id: UUID,
    version_id: int,
    service: EndpointService = Depends(get_endpoint_service),
) -> Dict[str, Any]:
    version = service.get_one_version(resource_id=_id, version_id=version_id)
    return version.data if version.data is not None else version.bundle_meta


@router.get("/{_id}/_history")
@router.get("/_history")
def get_endpoint_history(
    _id: UUID | None = None,
    _since: HistoryRequest = Depends(),
    service: MatchingCareService = Depends(get_matching_care_service),
) -> Dict[str, Any]:
    history = service.find_endpoint_history(endpoint_id=_id, since=_since.since)
    return history


@router.get("/{_id}")
def get_endpoint(
    _id: UUID,
    service: EndpointService = Depends(get_endpoint_service),
) -> Dict[str, Any] | None:
    endpoint = service.get_one(_id)
    return endpoint.data
