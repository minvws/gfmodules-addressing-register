import unittest
from contextlib import contextmanager
from typing import Generator

import inject
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.application import create_fastapi_app

from app.data import UraNumber
from app.models.supplier.dto import UpdateSupplierRequest
from app.models.supplier.model import SupplierModel, UraNumberModel

from app.config import set_config
from test_config import get_test_config_with_postgres_db_connection, get_postgres_database


@contextmanager
def temp_partial_config() -> Generator[None, None, None]:
    temp_test_config = get_test_config_with_postgres_db_connection()

    """Context manager to temporarily update a part of the config and reset afterward."""
    try:
        temp_test_config.app.override_authentication_ura = None
        set_config(temp_test_config)
        yield None
    finally:
        # Revert to the original configuration
        temp_test_config.app.override_authentication_ura = "00000000"
        set_config(temp_test_config)


class BaseTestApi(unittest.TestCase):

    def setUp(self) -> None:
        temp_partial_config()
        app: FastAPI = create_fastapi_app()
        self.client: TestClient = TestClient(app)
        database = get_postgres_database()
        assert database.is_healthy()
        database.generate_tables()
        database.truncate_tables()

    def tearDown(self) -> None:
        inject.clear()

    """Base class for setting up FastAPI app and client."""
    @staticmethod
    def create_test_supplier(ura_number: str = "12345678",
                             care_provider_name: str = "test",
                             update_supplier_endpoint: str = "test") -> SupplierModel:
        """Fixture to create a SupplierModel for tests."""
        return SupplierModel(
            ura_number=UraNumber(ura_number),
            care_provider_name=care_provider_name,
            update_supplier_endpoint=update_supplier_endpoint
        )

    @staticmethod
    def create_test_ura_number(ura_number: str = "12345678") -> UraNumberModel:
        """Fixture to create a UraNumberModel for tests."""
        return UraNumberModel(ura_number=UraNumber(ura_number))

    @staticmethod
    def create_update_query(ura_number: str = "12345678",
                             care_provider_name: str = "updated",
                             update_supplier_endpoint: str = "updated") -> UpdateSupplierRequest:
        return UpdateSupplierRequest(
            ura_number=UraNumber(ura_number),
            care_provider_name=care_provider_name,
            update_supplier_endpoint=update_supplier_endpoint
        )

    def create_supplier(self) -> SupplierModel:
        supplier = self.create_test_supplier()
        self.client.post("/supplier/", json=supplier.model_dump())
        return supplier


class TestHealthCheck(BaseTestApi):

    def test_main(self) -> None:
        """Test database health check."""
        health_check_response = self.client.get("/health")
        self.assertEqual(health_check_response.status_code, 200, "Unexpected response code")
        self.assertEqual(health_check_response.json(), {
            "status": "ok",
            "components": {
                "database": "ok"
            }
        })

        """Test main page retrieval."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class TestAddSupplier(BaseTestApi):

    def test_add_supplier(self) -> None:
        """Test adding a supplier."""
        current_config = get_test_config_with_postgres_db_connection()
        current_config.app.override_authentication_ura = "00000000"
        set_config(current_config)

        expected_supplier = self.create_test_supplier()
        response = self.client.post("/supplier/", json=expected_supplier.model_dump())
        self.assertEqual(response.status_code, 201)
        actual_supplier = SupplierModel(**response.json())
        self.assertEqual(actual_supplier.ura_number, expected_supplier.ura_number)
        self.assertEqual(actual_supplier.care_provider_name, expected_supplier.care_provider_name)
        self.assertEqual(actual_supplier.update_supplier_endpoint, expected_supplier.update_supplier_endpoint)

    def test_add_supplier_should_fail_due_to_missing_certificates(self) -> None:
        """Test failure when adding a supplier due to missing certificates."""
        with temp_partial_config():
            response = self.client.post("/supplier/")
            self.assertEqual(response.status_code, 401)

    def test_add_supplier_should_fail_due_to_duplicate_endpoint(self) -> None:
        """Test failure when adding a duplicate supplier."""
        supplier = self.create_test_supplier()
        response = self.client.post("/supplier/", json=supplier.model_dump())
        self.assertEqual(response.status_code, 201)
        response = self.client.post("/supplier/", json=supplier.model_dump())
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json().get("detail"),
                         "Care provider already has an update supplier endpoint set up, cannot have more than one")

    def test_add_supplier_should_fail_due_to_missing_or_invalid_supplier_data(self) -> None:
        """Test failure when adding supplier with missing or invalid data."""
        response = self.client.post("/supplier/")
        self.assertEqual(response.status_code, 422)


class TestGetSupplier(BaseTestApi):

    def test_get_supplier(self) -> None:
        """Test retrieving an existing supplier."""
        expected_supplier = self.create_supplier()
        response = self.client.post("/supplier/get-update-supplier",
                                    json=self.create_test_ura_number().model_dump())
        self.assertEqual(response.status_code, 200)
        actual_supplier = SupplierModel(**response.json())
        self.assertEqual(actual_supplier, expected_supplier)

    def test_get_supplier_should_fail_due_to_missing_certificates(self) -> None:
        """Test failure when retrieving supplier due to missing certificates."""
        with temp_partial_config():
            response = self.client.post("/supplier/get-update-supplier")
            self.assertEqual(response.status_code, 401)

    def test_get_supplier_should_fail_due_to_missing_ura_number(self) -> None:
        """Test failure when retrieving supplier due to missing URA number."""
        response = self.client.post("/supplier/get-update-supplier")
        self.assertEqual(response.status_code, 422)

    def test_get_supplier_should_fail_due_to_invalid_ura_number(self) -> None:
        """Test failure when retrieving supplier due to invalid URA number."""
        response = self.client.post(
            "/supplier/get-update-supplier",
            json=UraNumberModel(ura_number=UraNumber("00000000")).model_dump()
        )
        self.assertEqual(response.status_code, 404)


class TestUpdateSupplier(BaseTestApi):

    def test_update_supplier(self) -> None:
        """Test updating an existing supplier."""
        self.create_supplier()
        supplier_request = self.create_update_query()
        response = self.client.patch("/supplier/", json=supplier_request.model_dump())
        self.assertEqual(response.status_code, 200)
        actual_supplier = SupplierModel(**response.json())
        self.assertEqual(actual_supplier.ura_number, UraNumber("12345678"))
        self.assertEqual(actual_supplier.care_provider_name, supplier_request.care_provider_name)
        self.assertEqual(actual_supplier.update_supplier_endpoint, supplier_request.update_supplier_endpoint)

    def test_update_supplier_should_fail_due_to_missing_certificates(self) -> None:
        """Test failure when updating supplier due to missing certificates."""
        with temp_partial_config():
            supplier_request = self.create_update_query()
            response = self.client.patch("/supplier/", json=supplier_request.model_dump())
            self.assertEqual(response.status_code, 401)

    def test_update_supplier_should_fail_due_to_invalid_ura_number(self) -> None:
        """Test failure when updating supplier due to invalid URA number."""
        supplier_request = self.create_update_query(ura_number="00000000")
        response = self.client.patch("/supplier/", json=supplier_request.model_dump())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json().get("detail"), "Requested resource was not found")


class TestDeleteSupplier(BaseTestApi):

    def test_delete_supplier(self) -> None:
        """Test deleting an existing supplier."""
        self.create_supplier()
        response = self.client.request('DELETE', "/supplier",
                                       json=self.create_test_ura_number().model_dump())
        self.assertEqual(response.status_code, 204)

    def test_delete_supplier_should_fail_due_to_missing_certificates(self) -> None:
        """Test failure when deleting supplier due to missing certificates."""
        with temp_partial_config():
            response = self.client.request('DELETE', "/supplier",
                                           json=self.create_test_ura_number().model_dump())
            self.assertEqual(response.status_code, 401)

    def test_delete_supplier_should_fail_due_to_invalid_ura_number(self) -> None:
        """Test failure when deleting supplier due to invalid URA number."""
        response = self.client.request('DELETE', "/supplier",
                                       json=self.create_test_ura_number().model_dump())
        self.assertEqual(response.status_code, 404)
