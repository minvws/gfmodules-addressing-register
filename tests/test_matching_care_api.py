from fastapi.testclient import TestClient
from fhir.resources.R4B.bundle import Bundle

from app.data import ConnectionType, EndpointStatus, UraNumber
from app.models.organization.model import OrganizationModel
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService
from utils import check_key_value


def test_organization_returns_fhir_bundle(
    client: TestClient, org_endpoint: str
) -> None:
    response = client.get(org_endpoint)
    assert response.status_code == 200
    bundle = Bundle.parse_raw(response.text)
    assert isinstance(bundle, Bundle)


def test_organization_returns_correct_organization(
    client: TestClient, org_endpoint: str, organization_service: OrganizationService
) -> None:
    expected_org = organization_service.add_one(
        OrganizationModel(
            ura_number=UraNumber(00000000),
            active=True,
            name="test_name",
            description="test_description",
        )
    )
    response = client.get(org_endpoint)
    assert response.status_code == 200
    bundle = Bundle.parse_raw(response.text)
    assert isinstance(bundle, Bundle)
    assert check_key_value(response.json(), "value", str(expected_org.id))


def test_organization_returns_422(client: TestClient, org_endpoint: str) -> None:
    response = client.get(org_endpoint, params="_id=0")
    assert response.status_code == 422


def test_endpoint_returns_fhir_bundle(
    client: TestClient, endpoint_endpoint: str
) -> None:
    response = client.get(endpoint_endpoint)
    assert response.status_code == 200
    bundle = Bundle.parse_raw(response.text)
    assert isinstance(bundle, Bundle)


def test_endpoint_returns_correct_endpoint(
    client: TestClient, endpoint_endpoint: str, endpoint_service: EndpointService
) -> None:
    expected_endpoint = endpoint_service.add_one(
        name="test_name",
        description="test_description",
        address="https://example.com/",
        status_type=EndpointStatus.Active,
        organization_id=None,
        connection_type=ConnectionType.DicomWadoRs,
        payload_type="none",
        payload_mime_type="application/json",
    )
    response = client.get(endpoint_endpoint)
    assert response.status_code == 200
    bundle = Bundle.parse_raw(response.text)
    assert isinstance(bundle, Bundle)
    assert check_key_value(response.json(), "id", str(expected_endpoint.id))


def test_endpoint_returns_422(client: TestClient, endpoint_endpoint: str) -> None:
    response = client.get(endpoint_endpoint, params="_id=0")
    assert response.status_code == 422
