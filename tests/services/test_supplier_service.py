from _pytest.python_api import raises
from starlette.exceptions import HTTPException

from app.data import UraNumber
from app.db.db import Database
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.models.supplier.dto import UpdateSupplierRequest
from app.services.supplier_service import SupplierService
from tests.utils import add_supplier, create_supplier


def test_create_supplier(supplier_service: SupplierService, setup_sqlite_database: Database) -> None:
    expected = create_supplier()
    actual = supplier_service.add_one(expected)
    assert expected == actual

def test_create_should_fail_due_to_duplicate(supplier_service: SupplierService, setup_sqlite_database: Database) -> None:
    expected = supplier_service.add_one(create_supplier())
    with raises(expected_exception=HTTPException) as context:
        supplier_service.add_one(expected)
    assert "Care provider already has an update supplier endpoint set up, cannot have more than one" in context.value.__str__()

def test_get_one_supplier_endpoint(supplier_service: SupplierService, setup_sqlite_database: Database) -> None:
    expected_endpoint = add_supplier(supplier_service)
    actual_endpoint = supplier_service.get_one(expected_endpoint.ura_number)
    assert actual_endpoint is not None
    assert expected_endpoint.model_dump() == actual_endpoint.model_dump()

def test_get_should_fail_due_to_non_existent(supplier_service: SupplierService, setup_sqlite_database: Database) -> None:
    with raises(ResourceNotFoundException):
        supplier_service.get_one(UraNumber("12345678"))

def test_update_supplier(supplier_service: SupplierService, setup_sqlite_database: Database) -> None:
    _ = add_supplier(supplier_service)

    expected_endpoint = supplier_service.update_one(
        UpdateSupplierRequest(
            ura_number=UraNumber("12345678"),
            care_provider_name="updated",
            update_supplier_endpoint="updated"
        )
    )
    actual_endpoint = supplier_service.get_one(UraNumber("12345678"))

    assert expected_endpoint.model_dump() == actual_endpoint.model_dump()

def test_delete_supplier(supplier_service: SupplierService, setup_sqlite_database: Database) -> None:
    expected_endpoint = add_supplier(supplier_service)
    assert supplier_service.get_one(expected_endpoint.ura_number) is not None
    supplier_service.delete_one(expected_endpoint.ura_number)
    with raises(ResourceNotFoundException):
        supplier_service.get_one(expected_endpoint.ura_number)

