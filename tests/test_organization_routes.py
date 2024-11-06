import pytest
from fastapi.testclient import TestClient
from fhir.resources.R4B.bundle import Bundle
from utils import add_organization, check_key_value

from app.db.db import Database
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService


@pytest.mark.parametrize(
    "endpoint_suffix, expected_type",
    [
        ("", "searchset"),
        ("/{id}", "searchset"),
        ("/_history", "history"),
        ("/{id}/_history", "history"),
    ],
)
def test_organization_routes(
    client: TestClient,
    org_endpoint: str,
    organization_service: OrganizationService,
    endpoint_service: EndpointService,
    endpoint_suffix: str,
    expected_type: str,
    setup_database: Database
) -> None:
    setup_database.truncate_tables()

    expected, _ = add_organization(organization_service, endpoint_service)
    endpoint = org_endpoint + endpoint_suffix.format(id=expected.id)
    response = client.get(endpoint)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["type"] == expected_type
    assert check_key_value(data, "value", str(expected.id))
    bundle = Bundle.parse_raw(response.text)
    assert isinstance(bundle, Bundle)
