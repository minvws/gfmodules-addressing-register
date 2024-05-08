import unittest
from app.db.db import Database
from app.models.address.dto import AddressRequest, DeleteAddress
from app.models.address.model import Address, AddressURLParameters
from app.models.meta.model import Meta
from app.services.addressing_service import AddressingService


class TestGettingOneAddress(unittest.TestCase):
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
        mock_address_paramteres = AddressURLParameters(
            name="category",
            type="string",
            value="beeldbank",
            required=True,
            description="department",
        )
        expected_address = Address(
            provider_id="provider",
            data_domain="domain",
            endpoint="https://provider.example.com",
            request_type="GET",
            parameters=[mock_address_paramteres],
        )

        # act
        self.addresses_service.add_provider_address(expected_address)
        actual_address = self.addresses_service.get_provider_address(
            provider_id="provider", data_domain="domain"
        )

        # assert
        assert actual_address is not None
        self.assertDictEqual(expected_address.model_dump(), actual_address.model_dump())


class TestGettingManyAddresses(unittest.TestCase):

    def setUp(self) -> None:
        # setup database
        self.database = Database("sqlite:///:memory:")
        self.database.generate_tables()

        # setup addresses service
        self.addresses_service = AddressingService(self.database)

    def test_get_many_addresses(self) -> None:
        # arrange
        mock_address_paramteres = AddressURLParameters(
            name="category",
            type="string",
            value="beeldbank",
            required=True,
            description="department",
        )
        provider_address_1 = Address(
            provider_id="provider_1",
            data_domain="domain_1",
            endpoint="https://provider_1.example.com",
            request_type="GET",
            parameters=[mock_address_paramteres],
        )
        provider_address_2 = Address(
            provider_id="provider_2",
            data_domain="data_domain_2",
            endpoint="https://provider_2.example.com",
            request_type="POST",
            parameters=[mock_address_paramteres],
        )

        expected_results = [provider_address_1, provider_address_2]
        parameters = [
            AddressRequest(provider_id="provider_1", data_domain="domain_1"),
            AddressRequest(provider_id="provider_2", data_domain="data_domain_2"),
        ]

        # act
        self.addresses_service.add_many_addresses(expected_results)
        actual_results = self.addresses_service.get_many_providers_addresses(parameters)

        # assert
        self.assertEqual(expected_results, actual_results)


class TestDeleteOneAddress(unittest.TestCase):
    def setUp(self) -> None:
        # setup database
        self.database = Database("sqlite:///:memory:")
        self.database.generate_tables()

        # setup addresses service
        self.addresses_service = AddressingService(self.database)

    def test_delete_one_address(self) -> None:
        # arrange
        mock_address_paramteres = AddressURLParameters(
            name="category",
            type="string",
            value="beeldbank",
            required=True,
            description="department",
        )
        provider_address = Address(
            provider_id="provider",
            data_domain="domain",
            endpoint="https://provider.example.com",
            request_type="GET",
            parameters=[mock_address_paramteres],
        )

        meta = Meta(total=1)
        expected_results = DeleteAddress(meta=meta, data=provider_address)

        # act
        self.addresses_service.add_provider_address(provider_address)
        actual_results = self.addresses_service.remove_one_address(
            provider_id="provider", data_domain="domain"
        )

        # assert
        self.assertEqual(expected_results, actual_results)


class TestDeleteManyAddresses(unittest.TestCase):
    def setUp(self) -> None:
        # setup database
        self.database = Database("sqlite:///:memory:")
        self.database.generate_tables()

        # setup addresses service
        self.addresses_service = AddressingService(self.database)

    def test_delete_many_addresses(self) -> None:
        mock_address_paramteres = AddressURLParameters(
            name="category",
            type="string",
            value="beeldbank",
            required=True,
            description="department",
        )
        provider_address_1 = Address(
            provider_id="provider_1",
            data_domain="domain_1",
            endpoint="https://provider_1.example.com",
            request_type="GET",
            parameters=[mock_address_paramteres],
        )
        provider_address_2 = Address(
            provider_id="provider_2",
            data_domain="data_domain_2",
            endpoint="https://provider_2.examople.com",
            request_type="POST",
            parameters=[mock_address_paramteres],
        )
        parameters = [
            AddressRequest(provider_id="provider_1", data_domain="domain_1"),
            AddressRequest(provider_id="provider_2", data_domain="data_domain_2"),
        ]

        meta = Meta(total=2)
        providers_to_add = [provider_address_1, provider_address_2]
        expected_results = DeleteAddress(meta=meta, data=providers_to_add)

        # act
        self.addresses_service.add_many_addresses(providers_to_add)
        actual_results = self.addresses_service.remove_many_addresses(parameters)

        # assert
        self.assertEqual(expected_results, actual_results)
