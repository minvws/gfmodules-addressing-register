from typing import Sequence

from fhir.resources.R4B.bundle import Bundle, BundleEntry
from fhir.resources.R4B.endpoint import Endpoint

from app.db.entities.organization.organization import Organization
from app.exceptions.service_exceptions import ResourceNotFoundException


def create_organization_histories_bundled_resources(
    organization_entries: Sequence[Organization],
) -> list[BundleEntry]:
    listing = []
    for org in organization_entries:
        if org.bundle_meta is None:
            raise ResourceNotFoundException(f"Organization {org.fhir_id} bundle meta not found")
        listing.append(
            BundleEntry.construct(
                resource=org.data,
                request=org.bundle_meta.get("request"),
                response=org.bundle_meta.get("response"),
            )
        )
    return listing


def create_endpoint_bundled_resources(
    endpoints: Sequence[Endpoint],
) -> list[BundleEntry]:
    bundled_resources = []
    for endpoint in endpoints:
        bundled_resources.append(BundleEntry.construct(resource=endpoint))
    return bundled_resources


def create_fhir_bundle(
    bundled_entries: list[BundleEntry], bundle_type: str = "searchset"
) -> Bundle:
    return Bundle.construct(
        type=bundle_type, entry=bundled_entries, total=len(bundled_entries)
    )
