import unittest
import uuid

from app.db.entities.endpoint.endpoint import Endpoint
from app.db.entities.value_sets.endpoint_payload_types import EndpointPayloadType
from app.services.entity_services.endpoint_service import EndpointService
from app.services.organization_history_service import OrganizationHistoryService
from mypy.test.helpers import assert_equal

from app.config import set_config
from app.data import UraNumber, EndpointStatus as EndpointStatusEnum, ConnectionType as ConnectionTypeEnum
from app.db.db import Database
from app.db.entities.organization.organization import Organization
from app.exceptions.service_exceptions import (
    ResourceNotFoundException,
    ResourceNotAddedException,
)
from app.models.organization.model import OrganizationModel
from app.services.entity_services.organization_service import OrganizationService
from test_config import get_test_config


class BaseTestSuite(unittest.TestCase):
    database: Database
    history_service: OrganizationHistoryService
    organization_service: OrganizationService
    endpoint_service: EndpointService

    @classmethod
    def setUpClass(cls) -> None:
        set_config(get_test_config())
        cls.database = Database("sqlite:///:memory:")  # Set again for each class
        cls.database.generate_tables()
        cls.history_service = OrganizationHistoryService(cls.database)
        cls.organization_service = OrganizationService(
            cls.database, cls.history_service
        )  # Set again for each class
        cls.endpoint_service = EndpointService(
            cls.database, cls.history_service
        )
        assert cls.database.is_healthy()

    def add_organization(
        self,
        ura_number: str = "00000000",
        active: bool = False,
        name: str = "test_name",
        description: str = "test_dscr",
        parent_organization_id: uuid.UUID | None = None,
    ) -> Organization:
        organization = OrganizationModel(
            ura_number=UraNumber(ura_number),
            active=active,
            name=name,
            description=description,
            parent_organization_id=parent_organization_id,
        )
        return self.organization_service.add_one(organization)


class TestMissingParentOrganization(BaseTestSuite):
    def test_add_organization_should_fail_when_parent_organization_does_not_exist(
        self,
    ) -> None:
        with self.assertRaises(ResourceNotAddedException) as context:
            self.add_organization(parent_organization_id=uuid.uuid4())
            assert context.msg == "Parent organization not found"

    def test_get_many_should_fail_when_parent_organization_does_not_exist(self) -> None:
        with self.assertRaises(ResourceNotFoundException) as context:
            self.organization_service.get_many(parent_organization_id=uuid.uuid4())
            assert context.msg == "Parent organization not found"

    def test_update_should_fail_when_parent_organization_does_not_exist(self) -> None:
        expected1 = self.add_organization(name="abcdef")
        with self.assertRaises(ResourceNotFoundException) as context:
            self.organization_service.update_one(
                ura_number=UraNumber(expected1.ura_number),
                parent_org=uuid.uuid4(),
                active=True,
                name="abcdef",
                description="abcdef",
            )
            assert context.msg == "Parent organization not found"


class TestFindOrganization(BaseTestSuite):
    def test_find_organization_should_succeed_with_proper_values(self) -> None:
        expected1 = self.add_organization(name="abcdef")
        expected2 = self.add_organization(ura_number="1", name="abc")
        expected3 = self.add_organization(ura_number="2", name="a")

        actuals = self.organization_service.find(name="a")
        assert_equal(actuals[0].id, expected1.id)
        assert_equal(actuals[1].id, expected2.id)
        assert_equal(actuals[2].id, expected3.id)


class TestCreateOneOrganization(BaseTestSuite):
    def test_create_one_should_succeed_with_proper_values(self) -> None:
        expected = self.add_organization()
        actual = self.organization_service.get_one(UraNumber(expected.ura_number))
        self.assertEqual(expected.id, actual.id)

    def test_create_one_with_endpoint_should_succeed(self) -> None:
        test_endpoint = Endpoint.create_instance(
            address="example",
            status_type=EndpointStatusEnum.Active,
            connection_type=ConnectionTypeEnum.Hl7FhirMsg,
            payload_type=EndpointPayloadType(code="some code", definition="some definition", display="some display"),
        )
        org_model = OrganizationModel(
            ura_number=UraNumber("12345678"), name="example", active=True
        )
        expected = self.organization_service.add_one(org_model, [test_endpoint])
        actual = self.organization_service.get_one(
            ura_number=UraNumber(expected.ura_number)
        )
        assert actual.endpoints
        self.assertEqual(expected.id, actual.id)


class TestGetManyOrganizations(BaseTestSuite):
    def test_get_many_should_succeed_with_proper_values(self) -> None:
        expected_1 = self.add_organization(ura_number="1")
        expected_2 = self.add_organization(ura_number="2")
        expected_3 = self.add_organization(ura_number="3")
        actual_list = self.organization_service.get_many(name=expected_1.name)
        assert actual_list[0].id == expected_1.id
        assert actual_list[1].id == expected_2.id
        assert actual_list[2].id == expected_3.id

        actual_list = self.organization_service.get_many(
            ura_number=expected_2.ura_number
        )
        assert len(actual_list) == 1
        assert actual_list[0].id == expected_2.id

    def test_get_many_should_fail_due_to_no_resource(self) -> None:
        with self.assertRaises(ResourceNotFoundException):
            self.organization_service.get_many(name="Unknown name")


class TestGetOneOrganization(BaseTestSuite):
    def test_get_one_by_ura_should_succeed_with_proper_values(self) -> None:
        expected_1 = self.add_organization()
        actual = self.organization_service.get_one(
            ura_number=UraNumber(expected_1.ura_number)
        )
        assert_equal(expected_1.id, actual.id)

    def test_get_one_by_ura_should_fail_due_to_no_resource(self) -> None:
        with self.assertRaises(ResourceNotFoundException):
            self.organization_service.get_one(ura_number=UraNumber("12345678"))


class TestUpdateOrganization(BaseTestSuite):
    def test_update_one_should_succeed_with_proper_values(self) -> None:
        expected_1 = self.add_organization()
        actual = self.organization_service.update_one(
            ura_number=UraNumber(expected_1.ura_number),
            name="Updated_name",
            description="Updated_descr",
            parent_org=None,
            active=False,
        )
        expected_1 = self.organization_service.get_one(UraNumber(expected_1.ura_number))
        assert_equal(expected_1.id, actual.id)
        assert_equal(expected_1.ura_number, actual.ura_number)
        assert_equal(expected_1.name, actual.name)
        assert_equal(expected_1.description, actual.description)

    def test_update_one_with_endpoint_should_succeed_with_proper_values_and_replace_old_endpoints(self) -> None:
        test_endpoint_1 = Endpoint.create_instance(
            address="example",
            status_type=EndpointStatusEnum.Active,
            connection_type=ConnectionTypeEnum.Hl7FhirMsg,
            payload_type=EndpointPayloadType(code="some code", definition="some definition", display="some display"),
        )
        test_endpoint_2 = Endpoint.create_instance(
            address="example",
            status_type=EndpointStatusEnum.Active,
            connection_type=ConnectionTypeEnum.Hl7FhirMsg,
            payload_type=EndpointPayloadType(code="some code 2", definition="some definition 2", display="some display 2"),
        )
        org_model = OrganizationModel(
            ura_number=UraNumber("12345678"), name="example", active=True
        )

        expected = self.organization_service.add_one(org_model, [test_endpoint_1])
        actual = self.organization_service.update_one(ura_number=UraNumber(expected.ura_number), name="new name", endpoints=[test_endpoint_2])

        self.assertEqual(expected.id, actual.id)
        self.assertNotEqual(expected.name, actual.name)
        self.assertNotEqual(test_endpoint_1.id, actual.endpoints[0].id)

        with self.assertRaises(ResourceNotFoundException):
            self.endpoint_service.get_one(endpoint_id=test_endpoint_1.id)

    def test_update_one_should_fail_due_to_no_resource(self) -> None:
        with self.assertRaises(ResourceNotFoundException):
            self.organization_service.update_one(
                ura_number=UraNumber("12345678"),
                name="Updated_name",
                parent_org=None,
                active=False,
                description="Updated_descr",
            )


class TestDeleteOrganization(BaseTestSuite):
    def test_get_one_by_ura_should_fail_when_org_does_not_exist(self) -> None:
        expected_1 = self.add_organization()
        assert (
            self.organization_service.get_one(UraNumber(expected_1.ura_number))
            is not None
        )
        self.organization_service.delete_one(
            ura_number=UraNumber(expected_1.ura_number)
        )
        with self.assertRaises(ResourceNotFoundException):
            self.organization_service.get_one(UraNumber(expected_1.ura_number))

    def test_delete_one_should_fail_due_to_no_resource(self) -> None:
        with self.assertRaises(ResourceNotFoundException):
            self.organization_service.delete_one(ura_number=UraNumber("12345678"))
