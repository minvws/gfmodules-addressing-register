import unittest

from starlette.exceptions import HTTPException

from app.data import UraNumber
from app.db.db import Database
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.models.supplier.dto import UpdateSupplierRequest
from app.models.supplier.model import SupplierModel
from app.services.supplier_service import SupplierService
from app.config import set_config
from test_config import get_test_config


class BaseTestSuite(unittest.TestCase):
    database = Database("sqlite:///:memory:", create_tables=True) # needed here otherwise type-check fails
    supplier_service = SupplierService(database) # needed here otherwise type-check fails
    @classmethod
    def setUpClass(cls) -> None:
        set_config(get_test_config())
        cls.database = Database("sqlite:///:memory:", create_tables=True) # Set again for each class
        cls.supplier_service = SupplierService(cls.database) # Set again for each class
        assert cls.database.is_healthy()

    def add_supplier_endpoint(self, ura_number: str = "00000000", care_provider_name: str = "test",
                              update_supplier_endpoint: str = "test") -> SupplierModel:
        created_endpoint = SupplierModel(
            ura_number=UraNumber(ura_number),
            care_provider_name=care_provider_name,
            update_supplier_endpoint=update_supplier_endpoint
        )
        self.supplier_service.add_one(created_endpoint)
        return created_endpoint

class TestCreateSupplierEndpoint(BaseTestSuite):
    def test_create_endpoint(self) -> None:
        expected = SupplierModel(
            ura_number=UraNumber("00000000"),
            care_provider_name="test",
            update_supplier_endpoint="test"
        )
        actual = self.supplier_service.add_one(expected)
        # assert
        assert expected == actual

    def test_create_should_fail_due_to_duplicate(self) -> None:
        expected = SupplierModel(
            ura_number=UraNumber("00000000"),
            care_provider_name="test",
            update_supplier_endpoint="test"
        )
        # assert
        with self.assertRaises(expected_exception=HTTPException) as context:
            self.supplier_service.add_one(expected)
            assert context.exception.status_code == 400

class TestGetOneSupplierEndpoint(BaseTestSuite):
    def test_get_one_supplier_endpoint(self) -> None:
        expected_endpoint = self.add_supplier_endpoint()
        # act
        actual_endpoint = self.supplier_service.get_one(expected_endpoint.ura_number)
        # assert
        assert actual_endpoint is not None
        self.assertDictEqual(expected_endpoint.model_dump(), actual_endpoint.model_dump())

    def test_get_should_fail_due_to_non_existent(self) -> None:
        with self.assertRaises(ResourceNotFoundException):
            self.supplier_service.get_one(UraNumber("12345678"))

class TestUpdateSupplierEndpoint(BaseTestSuite):
    def test_update_supplier(self) -> None:
        self.add_supplier_endpoint()

        expected_endpoint = self.supplier_service.update_one(
            UpdateSupplierRequest(
                ura_number=UraNumber("00000000"),
                care_provider_name="test",
                update_supplier_endpoint="test"
            )
        )
        actual_endpoint = self.supplier_service.get_one(UraNumber("00000000"))

        self.assertDictEqual(expected_endpoint.model_dump(), actual_endpoint.model_dump())

    def test_get_should_fail_due_to_non_existent(self) -> None:
        with self.assertRaises(ResourceNotFoundException):
            self.supplier_service.get_one(UraNumber("12345678"))

class TestDeleteSupplierEndpoint(BaseTestSuite):
    def test_delete_supplier(self) -> None:
        expected_endpoint = self.add_supplier_endpoint()
        # act & assert
        assert self.supplier_service.get_one(UraNumber("00000000")) is not None
        self.supplier_service.delete_one(expected_endpoint.ura_number)
        with self.assertRaises(ResourceNotFoundException):
            self.supplier_service.get_one(UraNumber("00000000"))

    def test_get_should_fail_due_to_non_existent(self) -> None:
        with self.assertRaises(ResourceNotFoundException):
            self.supplier_service.get_one(UraNumber("12345678"))
