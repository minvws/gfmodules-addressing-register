from datetime import datetime
from typing import Any, List, Sequence
from uuid import UUID

from fhir.resources.R4B.bundle import Bundle, BundleEntry
from fhir.resources.R4B.organization import Organization as FhirOrganization
from fhir.resources.R4B.reference import Reference

from app.db.entities.organization.organization import Organization
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.mappers.fhir_mapper import (
    BundleType,
    create_bundle_entries,
    create_fhir_bundle,
)
from app.params.endpoint_query_params import EndpointQueryParams
from app.params.organization_query_params import OrganizationQueryParams
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService


class MatchingCareService:
    def __init__(
        self,
        organization_service: OrganizationService,
        endpoint_service: EndpointService,
    ) -> None:
        self._organization_service = organization_service
        self._endpoint_service = endpoint_service

    def find_organizations_history(
        self, organization_id: UUID | None = None, since: datetime | None = None
    ) -> dict[str, Any]:
        organization_entries = self._organization_service.find(
            id=organization_id, sort_history=True, since=since
        )

        return create_fhir_bundle(  # type: ignore
            bundled_entries=create_bundle_entries(
                organization_entries, with_req_resp=True
            ),
            bundle_type=BundleType.HISTORY,
        ).dict()

    def find_organizations(self, org_query_request: OrganizationQueryParams) -> Bundle:
        organizations = self._organization_service.find(
            latest_version=True,
            **org_query_request.model_dump(
                exclude={"include", "rev_include", "updated_at"}
            ),
        )

        bundled_resources = create_bundle_entries(organizations, with_req_resp=True)

        include_endpoints = True if org_query_request.include is not None else False
        if include_endpoints:
            bundled_resources = self._include_endpoints(
                bundled_resources, organizations
            )

        return create_fhir_bundle(
            bundled_entries=bundled_resources, bundle_type=BundleType.SEARCHSET
        )

    def find_endpoints(self, endpoints_req_params: EndpointQueryParams) -> Bundle:
        endpoints = self._endpoint_service.find(
            latest_version=True, **endpoints_req_params.model_dump()
        )

        return create_fhir_bundle(
            bundled_entries=create_bundle_entries(endpoints, with_req_resp=False),
            bundle_type=BundleType.SEARCHSET,
        )

    def find_endpoint_history(
        self, endpoint_id: UUID | None = None, since: datetime | None = None
    ) -> dict[str, Any]:
        endpoints = self._endpoint_service.find(
            id=endpoint_id, sort_history=True, since=since
        )

        return create_fhir_bundle(  # type: ignore
            bundled_entries=create_bundle_entries(endpoints, with_req_resp=True),
            bundle_type=BundleType.HISTORY,
        ).dict()

    def _include_endpoints(
        self, bundled_resources: List[BundleEntry], orgs: Sequence[Organization]
    ) -> List[BundleEntry]:
        for org in orgs:
            if org.data is None:
                raise ResourceNotFoundException("Data not found in resource")
            fhir_org = FhirOrganization(**org.data)
            if fhir_org.endpoint is None:
                continue

            for ref in fhir_org.endpoint:
                if not isinstance(ref, Reference):
                    raise TypeError("reference not correct type")
                endpoint_id = ref.reference.replace("Endpoint/", "")
                endpoint = self._endpoint_service.get_one(UUID(endpoint_id))
                bundled_resources.append(BundleEntry.construct(resource=endpoint.data))

        return bundled_resources
