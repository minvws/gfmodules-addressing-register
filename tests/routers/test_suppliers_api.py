from typing import Generator

from starlette.testclient import TestClient

from app.models.supplier.model import SupplierModel
from tests.utils import check_key_value, create_supplier


def test_add_supplier(
    sqlite_client: TestClient,
    supplier_endpoint: str,
    override_ura: Generator[None, None, None],
) -> None:
    expected_supplier = create_supplier()
    response = sqlite_client.post(
        supplier_endpoint, json=expected_supplier.model_dump()
    )
    assert response.status_code == 201
    actual_supplier = dict(response.json())
    exp_supplier_dict = expected_supplier.model_dump()
    assert actual_supplier["ura_number"] == exp_supplier_dict["ura_number"]
    assert (
        actual_supplier["care_provider_name"] == exp_supplier_dict["care_provider_name"]
    )
    assert (
        actual_supplier["update_supplier_endpoint"]
        == exp_supplier_dict["update_supplier_endpoint"]
    )


def test_add_supplier_should_fail_due_to_missing_certificates(
    sqlite_client: TestClient,
    supplier_endpoint: str,
) -> None:
    """Test failure when adding a supplier due to missing certificates."""
    response = sqlite_client.post(supplier_endpoint, json={})
    assert response.status_code == 401


def test_add_supplier_should_fail_due_to_duplicate_endpoint(
    sqlite_client: TestClient,
    supplier_endpoint: str,
    override_ura: Generator[None, None, None],
) -> None:
    """Test failure when adding a duplicate supplier."""
    supplier = create_supplier()
    response = sqlite_client.post(supplier_endpoint, json=supplier.model_dump())
    assert response.status_code == 201
    response = sqlite_client.post(supplier_endpoint, json=supplier.model_dump())
    assert response.status_code == 409
    assert check_key_value(
        response.json(),
        "text",
        "Care provider already has an update supplier endpoint set up, cannot have more than one",
    )


def test_add_supplier_should_fail_due_to_missing_or_invalid_supplier_data(
    sqlite_client: TestClient,
    supplier_endpoint: str,
    override_ura: Generator[None, None, None],
) -> None:
    """Test failure when adding supplier with missing or invalid data."""
    response = sqlite_client.post(supplier_endpoint, json={})
    assert response.status_code == 422


def test_get_supplier(
    sqlite_client: TestClient,
    supplier_endpoint: str,
    override_ura: Generator[None, None, None],
) -> None:
    """Test retrieving an existing supplier."""
    sqlite_client.post(supplier_endpoint, json=create_supplier().model_dump())
    expected_supplier = create_supplier().model_dump()
    response = sqlite_client.post(
        f"{supplier_endpoint}/get-update-supplier", json=expected_supplier
    )
    assert response.status_code == 200
    actual_supplier = SupplierModel(**response.json()).model_dump()
    assert actual_supplier == expected_supplier


def test_get_supplier_should_fail_due_to_missing_certificates(
    sqlite_client: TestClient, supplier_endpoint: str
) -> None:
    """Test failure when retrieving supplier due to missing certificates."""
    response = sqlite_client.post(f"{supplier_endpoint}/get-update-supplier")
    assert response.status_code == 401


def test_get_supplier_should_fail_due_to_missing_ura_number(
    sqlite_client: TestClient,
    supplier_endpoint: str,
    override_ura: Generator[None, None, None],
) -> None:
    """Test failure when retrieving supplier due to missing URA number."""
    response = sqlite_client.post(f"{supplier_endpoint}/get-update-supplier")
    assert response.status_code == 422


def test_get_supplier_should_fail_due_to_invalid_ura_number(
    sqlite_client: TestClient,
    supplier_endpoint: str,
    override_ura: Generator[None, None, None],
) -> None:
    """Test failure when retrieving supplier due to invalid URA number."""
    response = sqlite_client.post(
        f"{supplier_endpoint}/get-update-supplier", json={"ura_number": "00000000"}
    )
    assert response.status_code == 404


def test_update_supplier(
    sqlite_client: TestClient,
    supplier_endpoint: str,
    override_ura: Generator[None, None, None],
) -> None:
    """Test updating an existing supplier."""
    sqlite_client.post(supplier_endpoint, json=create_supplier().model_dump())
    supplier_request = create_supplier(
        care_provider_name="updated", update_supplier_endpoint="updated"
    )
    response = sqlite_client.patch(
        supplier_endpoint, json=supplier_request.model_dump()
    )
    assert response.status_code == 200
    actual_supplier = SupplierModel(**response.json())
    assert actual_supplier.ura_number == supplier_request.ura_number
    assert actual_supplier.care_provider_name == supplier_request.care_provider_name
    assert (
        actual_supplier.update_supplier_endpoint
        == supplier_request.update_supplier_endpoint
    )


def test_update_supplier_should_fail_due_to_missing_certificates(
    sqlite_client: TestClient, supplier_endpoint: str
) -> None:
    """Test failure when updating supplier due to missing certificates."""
    response = sqlite_client.patch(supplier_endpoint, json={})
    assert response.status_code == 401


def test_update_supplier_should_fail_due_to_unknown_ura_number(
    sqlite_client: TestClient,
    supplier_endpoint: str,
    override_ura: Generator[None, None, None],
) -> None:
    """Test failure when updating supplier due to invalid URA number."""
    supplier_request = create_supplier(ura_number="00000000")
    response = sqlite_client.patch(
        supplier_endpoint, json=supplier_request.model_dump()
    )
    assert response.status_code == 404
    assert check_key_value(response.json(), "text", "Requested resource was not found")


def test_update_supplier_should_fail_due_to_missing_or_invalid_supplier_data(
    sqlite_client: TestClient,
    supplier_endpoint: str,
    override_ura: Generator[None, None, None],
) -> None:
    """Test failure when updating supplier with missing or invalid data."""
    response = sqlite_client.patch(supplier_endpoint, json={})
    assert response.status_code == 422


def test_delete_supplier(
    sqlite_client: TestClient,
    supplier_endpoint: str,
    override_ura: Generator[None, None, None],
) -> None:
    """Test deleting an existing supplier."""
    sqlite_client.post(supplier_endpoint, json=create_supplier().model_dump())
    response = sqlite_client.request(
        "DELETE", supplier_endpoint, json={"ura_number": "12345678"}
    )
    assert response.status_code == 204


def test_delete_supplier_should_fail_due_to_missing_certificates(
    sqlite_client: TestClient, supplier_endpoint: str
) -> None:
    """Test failure when deleting supplier due to missing certificates."""
    response = sqlite_client.request(
        "DELETE", supplier_endpoint, json={"ura_number": "12345678"}
    )
    assert response.status_code == 401


def test_delete_supplier_should_fail_due_to_invalid_ura_number(
    sqlite_client: TestClient,
    supplier_endpoint: str,
    override_ura: Generator[None, None, None],
) -> None:
    """Test failure when deleting supplier due to invalid URA number."""
    response = sqlite_client.request(
        "DELETE", supplier_endpoint, json={"ura_number": "00000000"}
    )
    assert response.status_code == 404
