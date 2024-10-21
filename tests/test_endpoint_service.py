import unittest
import uuid

from mypy.test.helpers import assert_equal

from app.config import set_config
from app.data import EndpointStatus, ConnectionType, UraNumber
from app.db.db import Database
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.entities.organization.organization import Organization
from app.db.entities.value_sets.endpoint_payload_types import EndpointPayloadType
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.models.organization.model import OrganizationModel
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService
from test_config import get_test_config


class BaseTestSuite(unittest.TestCase):
    database = Database("sqlite:///:memory:")  # needed here otherwise type-check fails
    endpoint_service = EndpointService(database)  # needed here otherwise type-check fails
    default_org: Organization = Organization()

    @classmethod
    def setUpClass(cls) -> None:
        set_config(get_test_config())
        cls.database = Database("sqlite:///:memory:")  # Set again for each class
        cls.database.generate_tables()
        cls.endpoint_service = EndpointService(cls.database)  # Set again for each class
        organization_service = OrganizationService(cls.database)
        assert cls.database.is_healthy()

        create_organization = OrganizationModel(
            ura_number=UraNumber("0"), active=True, name="name", description="description",
            parent_organization_id=None,
        )

        with cls.database.get_db_session() as session:
            session.add(
                EndpointPayloadType(
                    code="none",
                    definition="none",
                    display="none"
                )
            )
            session.commit()

        cls.default_org = organization_service.add_one(organization=create_organization)

    def add_endpoint(self,
                     name: str = "test_name", description: str = "test_descr", address: str = "test_address",
                     status_type: str = "active", organization_id: uuid.UUID | None = None,
                     connection_type: str = 'hl7-fhir-rest') -> Endpoint:
        created_endpoint = self.endpoint_service.add_one(
            name=name, description=description, address=address, status_type=EndpointStatus(status_type),
            organization_id=organization_id, connection_type=ConnectionType(connection_type),
            payload_type="none", payload_mime_type="application/xml"
        )
        return created_endpoint


class TestFindEndpoint(BaseTestSuite):
    def test_find_endpoint_should_return_all_endpoints(self) -> None:
        expected1 = self.add_endpoint(organization_id=self.default_org.id)
        expected2 = self.add_endpoint(organization_id=self.default_org.id)
        expected3 = self.add_endpoint(organization_id=self.default_org.id)

        actuals = self.endpoint_service.find(organization_id=self.default_org.id)
        assert_equal(actuals[0].id, expected1.id)
        assert_equal(actuals[1].id, expected2.id)
        assert_equal(actuals[2].id, expected3.id)


class TestMissingOrganization(BaseTestSuite):
    def test_add_should_fail_with_missing_organization(self) -> None:
        with self.assertRaises(ResourceNotFoundException):
            self.add_endpoint(organization_id=uuid.uuid4())

    def test_get_many_should_fail_with_missing_organization(self) -> None:
        with self.assertRaises(ResourceNotFoundException):
            self.endpoint_service.get_many(organization_id=uuid.uuid4())

    def test_update_should_fail_with_missing_organization(self) -> None:
        endpoint = self.add_endpoint()
        with self.assertRaises(ResourceNotFoundException):
            self.endpoint_service.update_one(endpoint_id=endpoint.id, organization_id=uuid.uuid4(),
                                             name="Updated_name", description="Updated_descr",
                                             address="Updated_address", status_type=EndpointStatus.Active)


class TestCreateOneEndpoint(BaseTestSuite):
    def test_create_one_should_succeed_with_proper_values(self) -> None:
        expected = self.add_endpoint()
        actual = self.endpoint_service.get_one(expected.id)
        self.assertEqual(expected.id, actual.id)


class TestGetManyEndpoints(BaseTestSuite):
    def test_get_many_should_succeed_with_proper_values(self) -> None:
        expected_1 = self.add_endpoint()
        expected_2 = self.add_endpoint(description="abc")
        expected_3 = self.add_endpoint()
        actual_list = self.endpoint_service.get_many(name=expected_1.name)
        assert actual_list[0].id == expected_1.id
        assert actual_list[1].id == expected_2.id
        assert actual_list[2].id == expected_3.id

        actual_list = self.endpoint_service.get_many(description="abc")
        assert len(actual_list) == 1
        assert actual_list[0].id == expected_2.id

    def test_get_many_should_fail_due_to_no_resource(self) -> None:
        with self.assertRaises(ResourceNotFoundException):
            self.endpoint_service.get_many(name="Unknown name")


class TestGetOneEndpoint(BaseTestSuite):
    def test_get_one_should_succeed_with_proper_values(self) -> None:
        expected_1 = self.add_endpoint()
        actual = self.endpoint_service.get_one(
            endpoint_id=expected_1.id
        )
        assert_equal(expected_1.id, actual.id)

    def test_get_one_should_fail_due_to_no_resource(self) -> None:
        with self.assertRaises(ResourceNotFoundException):
            self.endpoint_service.get_one(endpoint_id=uuid.uuid4())


class TestUpdateEndpoint(BaseTestSuite):
    def test_update_one_should_succeed_with_proper_values(self) -> None:
        expected_1 = self.add_endpoint()
        actual = self.endpoint_service.update_one(endpoint_id=expected_1.id,
                                                  name="Updated_name", description="Updated_descr",
                                                  address="Updated_address",
                                                  organization_id=None, status_type=EndpointStatus.Active)
        expected_1 = self.endpoint_service.get_one(expected_1.id)
        assert_equal(expected_1.id, actual.id)
        assert_equal(expected_1.name, actual.name)
        assert_equal(expected_1.description, actual.description)
        assert_equal(expected_1.address, actual.address)
        assert_equal(expected_1.status_type, actual.status_type)
        assert_equal(expected_1.organization_id, actual.organization_id)

    def test_update_one_should_fail_due_to_no_resource(self) -> None:
        with self.assertRaises(ResourceNotFoundException):
            self.endpoint_service.update_one(endpoint_id=uuid.uuid4(), name="Updated_name",
                                             description="Updated_descr", address="Updated_address",
                                             status_type=EndpointStatus.Active, organization_id=None)


class TestDeleteEndpoint(BaseTestSuite):
    def test_delete_one_should_succeed_with_proper_values(self) -> None:
        expected_1 = self.add_endpoint()
        assert self.endpoint_service.get_one(expected_1.id) is not None
        self.endpoint_service.delete_one(endpoint_id=expected_1.id)
        with self.assertRaises(ResourceNotFoundException):
            self.endpoint_service.get_one(expected_1.id)

    def test_delete_one_should_fail_due_to_no_resource(self) -> None:
        with self.assertRaises(ResourceNotFoundException):
            self.endpoint_service.delete_one(endpoint_id=uuid.uuid4())
