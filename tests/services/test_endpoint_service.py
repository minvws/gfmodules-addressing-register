from uuid import uuid4

from _pytest.python_api import raises

from app.db.db import Database
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService
from seeds.generate_data import DataGenerator
from tests.utils import add_endpoint, add_organization


def test_get_one_correctly_finds_endpoint(endpoint_service: EndpointService) -> None:
    expected = add_endpoint(endpoint_service)
    actual = endpoint_service.get_one(endpoint_id=expected.fhir_id)
    assert actual.fhir_id == expected.fhir_id


def test_get_one_fails_correctly_when_no_endpoint_is_found(endpoint_service: EndpointService) -> None:
    random_id = uuid4()
    with raises(ResourceNotFoundException) as exc_info:
        _ = endpoint_service.get_one(endpoint_id=random_id)
    assert f"Endpoint not found for {random_id}" in str(exc_info.value)


def test_add_one_correctly_adds_endpoint(endpoint_service: EndpointService) -> None:
    dg = DataGenerator()
    expected = dg.generate_endpoint()
    actual = endpoint_service.add_one(expected)
    assert actual.data.get("address") == expected.address # type: ignore


def test_add_one_correctly_adds_endpoint_with_managing_org(endpoint_service: EndpointService,
                                                           organization_service: OrganizationService, setup_postgres_database: Database) -> None:
    dg = DataGenerator()
    setup_postgres_database.truncate_tables()
    org = add_organization(organization_service)
    expected = dg.generate_endpoint(org_fhir_id=org.fhir_id)
    actual = endpoint_service.add_one(expected)
    assert actual.data.get("address") == expected.address # type: ignore
    assert actual.data.get("managingOrganization") == {"reference": f"Organization/{org.fhir_id}"} # type: ignore


def test_add_one_fails_correctly_when_managing_org_does_not_exist(endpoint_service: EndpointService) -> None:
    dg = DataGenerator()
    random_id=uuid4()
    expected = dg.generate_endpoint()
    expected.managingOrganization = {"reference": f"Organization/{random_id}"}  # type: ignore
    with raises(ResourceNotFoundException) as exc_info:
        endpoint_service.add_one(expected)
    assert f"Organization {random_id} was not found" in str(exc_info.value)


def test_delete_one_correctly_deletes_endpoint(endpoint_service: EndpointService) -> None:
    expected = add_endpoint(endpoint_service)
    assert endpoint_service.get_one(endpoint_id=expected.fhir_id).fhir_id.__str__() == expected.fhir_id.__str__()
    endpoint_service.delete_one(endpoint_id=expected.fhir_id)
    with raises(ResourceNotFoundException) as exc_info:
        endpoint_service.get_one(endpoint_id=expected.fhir_id)
    assert f"Endpoint not found for {expected.fhir_id}" in str(exc_info.value)


def test_delete_one_also_deletes_managing_org_reference(endpoint_service: EndpointService,
                                                        organization_service: OrganizationService, setup_postgres_database: Database) -> None:
    setup_postgres_database.truncate_tables()
    org = add_organization(organization_service)
    expected = add_endpoint(endpoint_service, org_fhir_id=org.fhir_id)
    assert organization_service.get_one(org.fhir_id).data.get("endpoint") == [ # type: ignore
        {"reference": f"Endpoint/{expected.fhir_id}"}]
    endpoint_service.delete_one(endpoint_id=expected.fhir_id)
    assert organization_service.get_one(org.fhir_id).data.get("endpoint") is None # type: ignore


def test_delete_one_correctly_fails_to_delete_endpoint_does_not_exist(endpoint_service: EndpointService) -> None:
    random_id = uuid4()
    with raises(ResourceNotFoundException) as exc_info:
        endpoint_service.delete_one(endpoint_id=random_id)
    assert f"Endpoint not found for {random_id}" in str(exc_info.value)


def test_update_one_correctly_updates_endpoint(endpoint_service: EndpointService) -> None:
    dg = DataGenerator()
    expected = dg.generate_endpoint(name="test_name")
    old_endpoint = add_endpoint(endpoint_service, complete_endpoint=expected.copy())
    actual = endpoint_service.update_one(endpoint_id=old_endpoint.fhir_id, endpoint_fhir=expected)
    assert old_endpoint.fhir_id.__str__() == actual.fhir_id.__str__()
    assert actual.data.get("name") == "test_name" # type: ignore


def test_update_one_correctly_updates_endpoint_with_managing_org(endpoint_service: EndpointService,
                                                                 organization_service: OrganizationService,setup_postgres_database: Database) -> None:
    setup_postgres_database.truncate_tables()
    dg = DataGenerator()
    expected = dg.generate_endpoint()
    old_endpoint = add_endpoint(endpoint_service, complete_endpoint=expected.copy())
    assert endpoint_service.get_one(old_endpoint.fhir_id).data.get( # type: ignore
        "managingOrganization") is None
    org = add_organization(organization_service)
    expected.managingOrganization = {"reference": f"Organization/{org.fhir_id}"} # type: ignore
    expected.id = str(old_endpoint.fhir_id)  # type: ignore
    actual = endpoint_service.update_one(endpoint_id=old_endpoint.fhir_id, endpoint_fhir=expected)
    assert old_endpoint.fhir_id.__str__() == actual.fhir_id.__str__()
    assert {"reference": f"Organization/{org.fhir_id}"} == endpoint_service.get_one(old_endpoint.fhir_id).data.get(  # type: ignore
        "managingOrganization")
    found_org = organization_service.get_one(org.fhir_id)
    endpoints = found_org.data.get("endpoint", [])  # type: ignore
    assert {"reference": f"Endpoint/{old_endpoint.fhir_id}"} in endpoints


def test_update_one_fails_correctly_when_endpoint_does_not_exist(endpoint_service: EndpointService) -> None:
    dg = DataGenerator()
    random_id = uuid4()
    with raises(ResourceNotFoundException) as exc_info:
        endpoint_service.update_one(endpoint_id=random_id, endpoint_fhir=dg.generate_endpoint())
    assert f"Endpoint not found for {random_id}" in str(exc_info.value)


def test_update_one_fails_correctly_managing_org_is_not_found(endpoint_service: EndpointService, setup_postgres_database: Database) -> None:
    setup_postgres_database.truncate_tables()
    dg = DataGenerator()
    broken_resource = dg.generate_endpoint()
    old_endpoint = add_endpoint(endpoint_service, complete_endpoint=broken_resource.copy())
    random_id = uuid4()
    with raises(ResourceNotFoundException) as exc_info:
        broken_resource.managingOrganization = {"reference": f"Organization/{random_id}"} # type: ignore
        endpoint_service.update_one(endpoint_id=old_endpoint.fhir_id, endpoint_fhir=broken_resource)
    assert f"Organization {random_id} was not found" in str(exc_info.value)
