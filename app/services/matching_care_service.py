from typing import Any, Sequence, List
from uuid import UUID

from fhir.resources.R4B.bundle import BundleEntry, Bundle
from fhir.resources.R4B.endpoint import Endpoint as FhirEndpoint
from fhir.resources.R4B.organization import Organization as FhirOrganization
from fhir.resources.R4B.reference import Reference

from app.db.entities.organization.organization import Organization
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.mappers.fhir_mapper import (
    create_fhir_bundle,
    create_endpoint_bundled_resources,
    create_organization_histories_bundled_resources,
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
        self, organization_id: UUID | None = None
    ) -> dict[str, Any]:
        organization_entries = self._organization_service.find(
            id=organization_id, sort_history=True
        )

        bundle_entries = create_organization_histories_bundled_resources(
            organization_entries
        )

        return create_fhir_bundle(  # type: ignore
            bundled_entries=bundle_entries,
            bundle_type="history",
        ).dict()

    def find_organizations(self, org_query_request: OrganizationQueryParams) -> Bundle:
        organizations = self._organization_service.find(
            latest_version=True,
            **org_query_request.model_dump(
                exclude={"include", "rev_include", "updated_at"}
            ),
        )

        bundled_resources = []
        for org in organizations:
            if org.bundle_meta is None:
                raise ResourceNotFoundException("Bundle meta data not found")
            bundled_resources.append(
                BundleEntry.construct(
                    resource=org.data,
                    request=org.bundle_meta.get("request"),
                    response=org.bundle_meta.get("response"),
                )
            )

        include_endpoints = True if org_query_request.include is not None else False
        if include_endpoints:
            bundled_resources = self._include_endpoints(
                bundled_resources, organizations
            )

        return create_fhir_bundle(bundled_entries=bundled_resources)

    def find_endpoints(self, endpoints_req_params: EndpointQueryParams) -> Bundle:
        endpoints = []
        for endpoint in self._endpoint_service.find(
            latest_version=True, **endpoints_req_params.model_dump()
        ):
            if endpoint.data is None:
                raise ResourceNotFoundException("Data not found in resource")
            endpoints.append(FhirEndpoint(**endpoint.data))

        bundled_endpoint_resources = create_endpoint_bundled_resources(endpoints)
        return create_fhir_bundle(bundled_entries=bundled_endpoint_resources)

    def find_endpoint_history(self, endpoint_id: UUID | None = None) -> dict[str, Any]:
        endpoints = self._endpoint_service.find(id=endpoint_id, sort_history=True)

        bundled_resources = []
        for endpoint in endpoints:
            if endpoint.bundle_meta is None:
                raise ResourceNotFoundException("Bundle meta data not found")
            bundled_resources.append(
                BundleEntry.construct(
                    resource=endpoint.data,
                    request=endpoint.bundle_meta.get("request"),
                    response=endpoint.bundle_meta.get("response"),
                )
            )

        return create_fhir_bundle(  # type: ignore
            bundled_entries=bundled_resources,
            bundle_type="history",
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
