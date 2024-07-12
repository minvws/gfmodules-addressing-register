import unittest

from app.data import DataDomain, ProviderID
from app.db.db import Database
from app.models.address.dto import AddressRequest, Meta, DeleteAddressResult
from app.models.address.model import Address, AddressURLParameters
from app.services.addressing_service import AddressingService
from app.config import set_config
from test_config import get_test_config

class BaseTestSuite(unittest.TestCase):
    def setUp(self) -> None:
        set_config(get_test_config())

        # setup database
        self.database = Database("sqlite:///:memory:")
        self.database.generate_tables()

        # setup addresses service
        self.addresses_service = AddressingService(self.database)


class TestGettingOneAddress(BaseTestSuite):
    def test_database_health(self) -> None:
        is_database_health = self.database.is_healthy()
        self.assertEqual(is_database_health, True)

    def test_get_one_address(self) -> None:
        # arrange
        mock_address_parameters = AddressURLParameters(
            name="category",
            type="string",
            value="beeldbank",
            required=True,
            description="department",
        )
        expected_address = Address(
            provider_id=ProviderID("1234"),
            data_domain=DataDomain.BeeldBank,
            endpoint="https://provider.example.com",
            request_type="GET",
            parameters=[mock_address_parameters],
        )

        # act
        self.addresses_service.add_provider_address(expected_address)
        actual_address = self.addresses_service.get_provider_address(
            provider_id=ProviderID("00001234"), data_domain=DataDomain.BeeldBank
        )

        # assert
        assert actual_address is not None
        self.assertDictEqual(expected_address.model_dump(), actual_address.model_dump())


class TestGettingManyAddresses(BaseTestSuite):
    def test_get_many_addresses(self) -> None:
        # arrange
        mock_address_parameters = AddressURLParameters(
            name="category",
            type="string",
            value="beeldbank",
            required=True,
            description="department",
        )
        provider_address_1 = Address(
            provider_id=ProviderID("1234"),
            data_domain=DataDomain.Medicatie,
            endpoint="https://provider_1.example.com",
            request_type="GET",
            parameters=[mock_address_parameters],
        )
        provider_address_2 = Address(
            provider_id=ProviderID("5312"),
            data_domain=DataDomain.BeeldBank,
            endpoint="https://provider_2.example.com",
            request_type="POST",
            parameters=[mock_address_parameters],
        )

        expected_results = [provider_address_1, provider_address_2]
        parameters = [
            AddressRequest(provider_id=ProviderID("1234"), data_domain=DataDomain.Medicatie),
            AddressRequest(provider_id=ProviderID("5312"), data_domain=DataDomain.BeeldBank),
        ]

        # act
        self.addresses_service.add_many_addresses(expected_results)
        actual_results = self.addresses_service.get_many_providers_addresses(parameters)

        # assert
        self.assertEqual(expected_results, actual_results)


class TestDeleteOneAddress(BaseTestSuite):
    def test_delete_one_address(self) -> None:
        # arrange
        mock_address_parameters = AddressURLParameters(
            name="category",
            type="string",
            value="beeldbank",
            required=True,
            description="department",
        )
        provider_address = Address(
            provider_id=ProviderID("1234"),
            data_domain=DataDomain.BeeldBank,
            endpoint="https://provider.example.com",
            request_type="GET",
            parameters=[mock_address_parameters],
        )

        expected_results = DeleteAddressResult(
            meta=Meta(total=1, deleted=1),
            addresses=[provider_address]
        )

        # act
        self.addresses_service.add_provider_address(provider_address)
        actual_results = self.addresses_service.remove_one_address(
            provider_id=ProviderID("1234"),
            data_domain=DataDomain.BeeldBank,
        )

        # assert
        self.assertEqual(expected_results, actual_results)


class TestDeleteManyAddresses(BaseTestSuite):
    def test_delete_many_addresses(self) -> None:
        mock_address_parameters = AddressURLParameters(
            name="category",
            type="string",
            value="beeldbank",
            required=True,
            description="department",
        )
        provider_address_1 = Address(
            provider_id=ProviderID("1234"),
            data_domain=DataDomain.BeeldBank,
            endpoint="https://provider_1.example.com",
            request_type="GET",
            parameters=[mock_address_parameters],
        )
        provider_address_2 = Address(
            provider_id=ProviderID("5312"),
            data_domain=DataDomain.Medicatie,
            endpoint="https://provider_2.example.com",
            request_type="POST",
            parameters=[mock_address_parameters],
        )
        parameters = [
            AddressRequest(provider_id=ProviderID("1234"), data_domain=DataDomain.BeeldBank),
            AddressRequest(provider_id=ProviderID("5312"), data_domain=DataDomain.Medicatie),
        ]

        meta = Meta(total=2, deleted=2)
        providers_to_add = [provider_address_1, provider_address_2]
        expected_results = DeleteAddressResult(meta=meta, addresses=providers_to_add)

        # act
        self.addresses_service.add_many_addresses(providers_to_add)
        actual_results = self.addresses_service.remove_many_addresses(parameters)

        # assert
        self.assertEqual(expected_results, actual_results)
