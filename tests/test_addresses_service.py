import unittest
from app.db.db import Database
from app.db.models.address import Address
from app.services.addressing_service import AddressingService


class TestAddressesService(unittest.TestCase):
    def setUp(self) -> None:
        # setup database
        self.database = Database("sqlite:///:memory:")
        self.database.generate_tables()

        # setup addresses service
        self.addresses_service = AddressingService(self.database)

    def test_database_health(self) -> None:
        is_database_health = self.database.is_healthy()
        self.assertEquals(is_database_health, True)

    def test_get_one_address(self) -> None:
        # arrange
        new_address_parameters = {
            "name": "category",
            "type": "string",
            "value": "beeldbank",
            "required": "true",
            "description": "department",
        }
        expected_address = Address(
            provider_id="provider",
            data_domain="domain",
            endpoint="https://provider.com",
            request_type="GET",
            parameters=[new_address_parameters],
        )

        # act
        self.addresses_service.add_provider_address(
            provider_id="provider",
            data_domain="domain",
            endpoint="https://provider.com",
            request_type="GET",
            parameters=[new_address_parameters],
        )
        actual_address = self.addresses_service.get_provider_addressing(
            provider_id="provider", data_domain="domain"
        )

        # assert
        assert actual_address is not None
        self.assertEqual(expected_address.provider_id, actual_address.provider_id)
        self.assertEqual(expected_address.data_domain, actual_address.data_domain)
        self.assertEqual(expected_address.endpoint, actual_address.endpoint)
        self.assertEqual(expected_address.request_type, actual_address.request_type)
        self.assertEqual(expected_address.parameters, actual_address.parameters)
