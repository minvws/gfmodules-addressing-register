from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.period import Period
from fhir.resources.R4B.reference import Reference

from app.db.entities.endpoint.endpoint import Endpoint as EndpointEntity
from app.db.entities.endpoint.endpoint_header import (
    EndpointHeader,
)
from app.db.entities.endpoint.endpoint_payload import (
    EndpointPayload,
)
from app.db.entities.organization.organization import Organization as OrganizationEntity
from app.db.entities.value_sets.connection_type import ConnectionType
from app.db.entities.value_sets.endpoint_payload_types import EndpointPayloadType
from app.mappers.fhir_mapper import map_to_endpoint_fhir, map_to_fhir_organization


@pytest.fixture
def mock_endpoint() -> EndpointEntity:
    endpoint_id = uuid4()
    return EndpointEntity(
        id=endpoint_id,
        name="example name",
        identifier="12345678",
        address="https://example.address.nl",
        connection_type="hl7-fhir-rest",
        status="active",
        connection=ConnectionType(code="hl7-fhir-rest", display="some-display"),
        period_start_date=datetime.now(),
        period_end_date=datetime.now() + timedelta(days=1),
        headers=[
            EndpointHeader(id=uuid4(), endpoint_id=endpoint_id, data="some header")
        ],
        payload=[
            EndpointPayload(
                id=uuid4(),
                endpoint_id=endpoint_id,
                payload_type="any",
                mime_type="some mime type",
                payload=EndpointPayloadType(code="any", display="payload of type any"),
            )
        ],
    )


@pytest.fixture()
def parent_organization() -> OrganizationEntity:
    return OrganizationEntity(
        id=uuid4(), name="example parent", ura_number="1234567", active=True
    )


@pytest.fixture()
def subsidiary_organization(
    parent_organization: OrganizationEntity,
) -> OrganizationEntity:
    return OrganizationEntity(
        id=uuid4(),
        name="subsidiary example",
        ura_number="456789",
        active=True,
        parent_organization_id=parent_organization.id,
        part_of=parent_organization,
    )


def test_map_to_fhir_organization_should_return_a_org_fhir_resource(
    subsidiary_organization: OrganizationEntity,
) -> None:
    expected = map_to_fhir_organization(subsidiary_organization, include_endpoints=True)
    assert isinstance(expected, Organization)
    assert isinstance(expected.identifier[0], Identifier) and isinstance(
        expected.identifier[1], Identifier
    )
    assert expected.identifier[0].value == subsidiary_organization.id.__str__()
    assert expected.identifier[1].value == subsidiary_organization.ura_number
    assert expected.name == subsidiary_organization.name
    assert subsidiary_organization.part_of is not None
    assert isinstance(expected.partOf, Reference)
    assert (
        expected.partOf.reference
        == f"Organization/{subsidiary_organization.part_of.ura_number}"
    )


def test_map_to_fhir_organization_should_return_a_org_fhir_resource_with_endpoints(
    subsidiary_organization: OrganizationEntity,
    mock_endpoint: EndpointEntity,
) -> None:
    subsidiary_organization.endpoints.append(mock_endpoint)
    expected = map_to_fhir_organization(subsidiary_organization, include_endpoints=True)
    assert isinstance(expected, Organization)
    assert isinstance(expected.identifier[0], Identifier) and isinstance(
        expected.identifier[1], Identifier
    )
    assert expected.identifier[0].value == subsidiary_organization.id.__str__()
    assert expected.identifier[1].value == subsidiary_organization.ura_number
    assert isinstance(expected.endpoint[0], Reference)
    assert expected.endpoint[0].reference == f"Endpoint/{mock_endpoint.id}"


def test_map_to_endpoint_fhir(
    subsidiary_organization: OrganizationEntity,
    mock_endpoint: EndpointEntity,
) -> None:
    mock_endpoint.organization_id = subsidiary_organization.id
    mock_endpoint.managing_organization = subsidiary_organization
    expected = map_to_endpoint_fhir(mock_endpoint)

    assert isinstance(expected, Endpoint)
    assert expected.id == mock_endpoint.id
    assert isinstance(expected.identifier[0], Identifier)
    assert expected.identifier[0].value == mock_endpoint.identifier
    assert expected.status == mock_endpoint.status_type
    assert isinstance(expected.connectionType, Coding)
    assert expected.connectionType.code == mock_endpoint.connection_type
    assert isinstance(expected.managingOrganization, Reference)
    assert (
        expected.managingOrganization.reference
        == f"Organization/{subsidiary_organization.ura_number}"
    )
    assert isinstance(expected.period, Period)
    assert expected.period.start == mock_endpoint.period_start_date
    assert expected.period.end == mock_endpoint.period_end_date
    assert expected.header[0] == mock_endpoint.headers[0].data
    assert mock_endpoint.payload is not None
    assert expected.payloadMimeType[0] == mock_endpoint.payload[0].mime_type
    assert isinstance(expected.payloadType[0], CodeableConcept) and isinstance(
        expected.payloadType[0].coding[0], Coding
    )
    assert (
        expected.payloadType[0].coding[0].code == mock_endpoint.payload[0].payload_type
    )
