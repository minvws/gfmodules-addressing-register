from typing import Sequence

from fhir.resources.R4B.bundle import Bundle, BundleEntry
from fhir.resources.R4B.organization import Organization

from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.reference import Reference
from fhir.resources.R4B.period import Period
from fhir.resources.R4B.contactpoint import ContactPoint

from app.db.entities.organization.organization import Organization as OrganizationEntity
from app.db.entities.endpoint.endpoint import Endpoint as EndpointEntity


def map_to_fhir_organization(
    entity: OrganizationEntity, include_endpoints: bool = False
) -> Organization:
    identifiers = [
        Identifier.construct(use="usual", value=entity.id.__str__()),
        Identifier.construct(use="official", value=entity.ura_number),
    ]
    part_of = (
        Reference.construct(reference=f"Organization/{entity.part_of.ura_number}")
        if entity.part_of
        else None
    )
    org_type = [
        CodeableConcept.construct(
            coding=[
                Coding.construct(
                    code=org_type.institution_type.code,
                    display=org_type.institution_type.display,
                )
            ],
            text="type of organization",
        )
        for org_type in entity.type
    ]
    endpoints = (
        [
            Reference.construct(reference=f"Endpoint/{endpoint.id}")
            for endpoint in entity.endpoints
        ]
        if include_endpoints
        else None
    )

    return Organization.construct(
        active=entity.active,
        name=entity.name,
        identifier=identifiers,
        type=org_type,
        partOf=part_of,
        endpoint=endpoints,
    )


def map_to_endpoint_fhir(entity: EndpointEntity) -> Endpoint:
    identifiers = [Identifier.construct(use="usual", value=entity.id.__str__())]
    connection_type = Coding.construct(
        code=entity.connection.code,
        display=entity.connection.display,
    )
    payload_types = (
        [
            CodeableConcept.construct(
                coding=[
                    Coding.construct(
                        code=pld_type.payload.code, display=pld_type.payload.display
                    )
                ],
                text="type of the payload for the endpoint",
            )
            for pld_type in entity.payload
        ]
        if entity.payload
        else None
    )
    managing_organization = (
        Reference.construct(
            reference=f"Organization/{entity.managing_organization.ura_number}"
        )
        if entity.managing_organization
        else None
    )
    payload_mime_type = (
        [p.mime_type for p in entity.payload] if entity.payload else None
    )
    contact = (
        [
            ContactPoint.construct(
                system=contact.contact_point.system_type,
                value=contact.contact_point.value,
                use=contact.contact_point.use_type,
                rank=contact.contact_point.rank,
                period=Period.construct(
                    start=contact.contact_point.period_start_date,
                    end=contact.contact_point.period_end_date,
                ),
            )
            for contact in entity.contacts
        ]
        if entity.contacts
        else None
    )
    period = Period.construct(
        start=entity.period_start_date,
        end=entity.period_end_date,
    )
    headers = [header.data for header in entity.headers]
    return Endpoint.construct(
        identifier=identifiers,
        status=entity.status_type,
        connectionType=connection_type,
        name=entity.name,
        managingOrganization=managing_organization,
        contact=contact,
        payloadType=payload_types,
        payloadMimeType=payload_mime_type,
        period=period,
        address=entity.address,
        header=headers,
    )


def create_organization_bundled_resources(
    organizations: Sequence[OrganizationEntity], include_endpoints: bool = False
) -> list[BundleEntry]:
    return [
        BundleEntry.construct(
            resource=(map_to_fhir_organization(org, include_endpoints))
        )
        for org in organizations
    ]


def create_endpoint_bundled_resources(
    endpoints: Sequence[EndpointEntity],
) -> list[BundleEntry]:
    return [
        BundleEntry.construct(resource=map_to_endpoint_fhir(endpoint))
        for endpoint in endpoints
    ]


def create_fhir_bundle(bundled_entries: list[BundleEntry]) -> Bundle:
    return Bundle.construct(
        type="searchset", entry=bundled_entries, total=len(bundled_entries)
    )
