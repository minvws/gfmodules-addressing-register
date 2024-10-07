from uuid import uuid4

import pytest
from fhir.resources.R4B.organization import Organization
from app.db.entities.organization.organization import Organization as OrganizationEntity
from app.db.entities.endpoint.endpoint import Endpoint as EndpointEntity
from app.mappers.fhir_mapper import map_to_fhir_organization


@pytest.fixture
def mock_endpoint() -> EndpointEntity:
    return EndpointEntity(
        id=uuid4(),
        name="example name",
        address="https://example.address.nl",
        connection_type="hl7-fhir-rest",
        status="active",
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


def test_map_to_fhir_organization_should_return_organization_fhir_resource(
    subsidiary_organization: OrganizationEntity,
) -> None:
    expected = map_to_fhir_organization(subsidiary_organization, include_endpoints=True)
    assert isinstance(expected, Organization)
    assert expected.identifier[0].value == subsidiary_organization.id.__str__()
    assert expected.identifier[1].value == subsidiary_organization.ura_number
    assert expected.name == subsidiary_organization.name
    assert (
        expected.partOf.reference
        == f"Organization/{subsidiary_organization.part_of.ura_number}"
    )


def test_map_to_fhir_should_return_a_organization_fhir_resource_with_endpoints(
    subsidiary_organization: OrganizationEntity,
    mock_endpoint: EndpointEntity,
):
    subsidiary_organization.endpoints.append(mock_endpoint)
    expected = map_to_fhir_organization(subsidiary_organization, include_endpoints=True)
    assert isinstance(expected, Organization)
    assert expected.identifier[0].value == subsidiary_organization.id.__str__()
    assert expected.identifier[1].value == subsidiary_organization.ura_number
    assert expected.endpoint[0].reference == f"Endpoint/{mock_endpoint.id}"
