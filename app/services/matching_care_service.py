from typing import Any

from app.mappers.fhir_mapper import (
    create_fhir_bundle,
    create_organization_bundled_resources,
    create_endpoint_bundled_resources,
)
from app.params.endpoint_query_params import EndpointQueryParams
from app.params.organization_query_params import OrganizationQueryParams
from app.services.entity_services.organization_service import OrganizationService
from app.services.entity_services.endpoint_service import EndpointService


class MatchingCareService:
    def __init__(
        self,
        organization_service: OrganizationService,
        endpoint_service: EndpointService,
    ) -> None:
        self._organization_service = organization_service
        self._endpoint_service = endpoint_service

    def find_organizations(
        self, org_query_request: OrganizationQueryParams
    ) -> dict[str, Any]:
        organizations = self._organization_service.find(
            **org_query_request.model_dump(
                exclude={"include", "rev_include", "updated_at"}
            ),
        )
        include_endpoints = True if org_query_request.include is not None else False
        bundled_organization_resources = create_organization_bundled_resources(
            organizations, include_endpoints
        )
        return create_fhir_bundle(bundled_entries=bundled_organization_resources).dict()  # type: ignore

    def find_endpoints(
        self, endpoints_req_params: EndpointQueryParams
    ) -> dict[str, Any]:
        endpoints = self._endpoint_service.find(**endpoints_req_params.model_dump())
        bundled_endpoint_resources = create_endpoint_bundled_resources(endpoints)
        return create_fhir_bundle(bundled_entries=bundled_endpoint_resources).dict()  # type: ignore
