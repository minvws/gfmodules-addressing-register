import logging
from typing import List

from app.data import UraNumber, DataDomain
from app.db.db import Database
from app.db.entities.address_entity import AddressEntity
from app.db.repositories.addresses_repository import (
    AddressesRepository,
)
from app.exceptions.service_exceptions import (
    ResourceNotDeletedException, ResourceNotFoundException, ResourceNotAddedException
)
from app.models.address.dto import Meta, DeleteAddressResult, AddressRequest
from app.models.address.model import Address, AddressURLParameters

logger = logging.getLogger(__name__)


class AddressingService:
    def __init__(self, database: Database):
        self.database = database

    def get_provider_address(
        self, ura_number: UraNumber, data_domain: DataDomain
    ) -> Address:
        with self.database.get_db_session() as session:
            addressing_repository = session.get_repository(AddressesRepository)
            entity = addressing_repository.find_one(
                ura_number=ura_number,
                data_domain=data_domain,
            )

            if entity is None:
                logging.warning(f"Address not found for {ura_number} {data_domain}")
                raise ResourceNotFoundException()

            return self.hydrate_address(entity)

    def get_many_providers_addresses(
        self, requested_addresses: List[AddressRequest]
    ) -> List[Address]:
        with self.database.get_db_session() as session:
            addressing_repository = session.get_repository(AddressesRepository)
            entities = addressing_repository.find_many(requested_addresses)
            if len(entities) == 0:
                logging.warning(f"Addresses not found for {requested_addresses}")
                raise ResourceNotFoundException()

            return [self.hydrate_address(entity) for entity in entities]

    def add_provider_address(self, address: Address) -> None:
        with self.database.get_db_session() as session:
            addressing_repository = session.get_repository(AddressesRepository)
            try:
                addressing_repository.create_one(address)
            except Exception as e:
                logging.error(f"Failed to add address {address}: {str(e)}")
                raise ResourceNotAddedException()

    def add_many_addresses(self, addresses: List[Address]) -> None:
        with self.database.get_db_session() as session:
            addressing_repository = session.get_repository(AddressesRepository)
            try:
                addressing_repository.create_many(addresses)
            except Exception as e:
                logging.error(f"Failed to add address {addresses}: {str(e)}")
                raise ResourceNotAddedException()

    def remove_one_address(
        self, ura_number: UraNumber, data_domain: DataDomain
    ) -> DeleteAddressResult:
        with self.database.get_db_session() as session:
            addressing_repository = session.get_repository(AddressesRepository)
            address = self.get_provider_address(ura_number, data_domain)
            if address is None:
                logging.warning(f"Address not found for {ura_number} {data_domain}")
                raise ResourceNotFoundException()

            delete_count = addressing_repository.delete_one(
                ura_number=ura_number, data_domain=data_domain
            )

            if delete_count == 0:
                logging.warning(f"Cannot remove address {ura_number} {data_domain}")
                raise ResourceNotDeletedException()

        return DeleteAddressResult(
            meta=Meta(total=1, deleted=1),
            addresses=[address],
        )

    def remove_many_addresses(
        self, requested_addresses: List[AddressRequest]
    ) -> DeleteAddressResult:
        with self.database.get_db_session() as session:
            addressing_repository = session.get_repository(AddressesRepository)
            addresses = self.get_many_providers_addresses(requested_addresses)

            delete_count = addressing_repository.delete_many(requested_addresses)
            if delete_count != len(addresses):
                raise ResourceNotDeletedException()

        return DeleteAddressResult(
            meta=Meta(
                total=len(addresses),
                deleted=delete_count,
            ),
            addresses=addresses,
        )

    @staticmethod
    def hydrate_address(entity: AddressEntity) -> Address:
        data_domain = DataDomain.from_str(entity.data_domain)
        if data_domain is None:
            raise ValueError("Invalid data domain")

        params = []
        for url_param in entity.parameters:
            params.append(AddressURLParameters(**url_param))

        return Address(
            ura_number=UraNumber(entity.ura_number),
            data_domain=data_domain,
            endpoint=entity.endpoint,
            request_type=entity.request_type,
            parameters=params,
        )
