from typing import List, Dict, Any

from app.mappers.fhir_mapper import map_to_fhir_organization, map_to_endpoint_fhir
from app.params.endpoint_query_params import EndpointQueryParams
from app.params.organization_query_params import OrganizationQueryParams
from app.services.organization_service import OrganizationService
from app.services.endpoint_service import EndpointService


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
    ) -> list[Dict[str, Any]]:
        organizations = self._organization_service.find(
            **org_query_request.model_dump(
                exclude={"include", "rev_include", "updated_at"}
            ),
        )
        include_endpoints = True if org_query_request.include is not None else False
        return [
            map_to_fhir_organization(org, include_endpoints).dict()
            for org in organizations
        ]

    def find_endpoints(
        self, endpoints_req_params: EndpointQueryParams
    ) -> List[Dict[str, Any]]:
        endpoints = self._endpoint_service.find(**endpoints_req_params.model_dump())
        return [map_to_endpoint_fhir(endpoint).dict() for endpoint in endpoints]
