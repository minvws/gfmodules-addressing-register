from typing import List, cast

from app.db.db import Database
from app.db.session import DbSession
from app.db.entities.address_entity import AddressEntity
from app.db.repositories.addresses_repository import AddressesRepository
from app.exceptions.service_exceptions import (
    AddressNotFoundException,
    UnsuccessfulAddException,
    UnsuccessfulDeleteOperationException,
)
from app.models.address.dto import DeleteAddress, AddressRequest
from app.models.address.model import Address
from app.models.meta.model import Meta


class AddressingService:
    def __init__(self, database: Database):
        self.database = database

    def get_provider_address(self, provider_id: str, data_domain: str) -> Address:
        with self.database.get_db_session() as session:
            addressing_repository = self.get_addressing_repository(session)
            address_entity = addressing_repository.find_one(
                provider_id=provider_id,
                data_domain=data_domain,
            )

            if address_entity is None:
                raise AddressNotFoundException()

            return Address(**address_entity.to_dict())

    def get_many_providers_addresses(
        self, requested_addresses: List[AddressRequest]
    ) -> List[Address]:
        with self.database.get_db_session() as session:
            addressing_repository = self.get_addressing_repository(session)
            results = addressing_repository.find_many(
                [address.model_dump() for address in requested_addresses]
            )
            if len(results) == 0:
                raise AddressNotFoundException()

            return [Address(**result.to_dict()) for result in results]

    def add_provider_address(self, new_address: Address) -> Address:
        with self.database.get_db_session() as session:
            addressing_repository = self.get_addressing_repository(session)
            result = addressing_repository.create_one(new_address=new_address.model_dump())
            if result is None:
                raise UnsuccessfulAddException()

            return Address(**result.to_dict())

    def add_many_addresses(self, addresses: List[Address]) -> List[Address]:
        with self.database.get_db_session() as session:
            addressing_repository = self.get_addressing_repository(session)
            results = addressing_repository.create_many(
                [address.model_dump() for address in addresses]
            )

            if results is None:
                raise UnsuccessfulAddException()

            return [Address(**result.to_dict()) for result in results]

    def remove_one_address(self, provider_id: str, data_domain: str) -> DeleteAddress:
        with self.database.get_db_session() as session:
            addressing_repository = self.get_addressing_repository(session)
            address = self.get_provider_address(provider_id, data_domain)

            deleted_row_count = addressing_repository.delete_one(
                provider_id=provider_id, data_domain=data_domain
            )
            if deleted_row_count == 0:
                raise UnsuccessfulDeleteOperationException()

            meta = Meta(total=deleted_row_count)
            return DeleteAddress(
                data=address,
                meta=meta,
            )

    def remove_many_addresses(
        self, requested_addresses: List[AddressRequest]
    ) -> DeleteAddress:
        with self.database.get_db_session() as session:
            addressing_repository = self.get_addressing_repository(session)
            addresses = self.get_many_providers_addresses(requested_addresses)

            if len(addresses) != len(requested_addresses):
                raise UnsuccessfulDeleteOperationException()

            results = addressing_repository.delete_many(
                [address.model_dump() for address in requested_addresses]
            )

            meta = Meta(total=results)

            return DeleteAddress(meta=meta, data=addresses)

    @staticmethod
    def get_addressing_repository(session: DbSession) -> AddressesRepository:
        """
        private method to get repository for providers
        """
        return cast(
            AddressesRepository,
            session.get_repository(AddressEntity)
        )