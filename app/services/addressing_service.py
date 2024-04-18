from typing import List, Dict

from app.db.db import Database
from app.db.db_session import DbSession
from app.db.models.address import Address
from app.db.repositories.addresses_repository import AddressesRepository


class AddressingService:
    def __init__(self, database: Database):
        self.database = database

    def get_provider_addressing(
        self, provider_id: str, data_domain: str
    ) -> Address | None:
        """
        Get one instance of a providers endpoint addresses
        """
        addressing_repository = self._get_addressing_repository()
        return addressing_repository.find_one_address(
            provider_id=provider_id, data_domain=data_domain
        )

    def add_provider_address(
        self,
        provider_id: str,
        data_domain: str,
        endpoint: str,
        request_type: str,
        parameters: List[Dict[str, str]],
    ) -> None:
        """
        Add a new provider endpoint addresses to the database. (This is only for testing purposes)
        """
        addressing_repository = self._get_addressing_repository()
        addressing_repository.add_one_address(
            provider_id=provider_id,
            data_domain=data_domain,
            endpoint=endpoint,
            request_type=request_type,
            parameters=parameters,
        )

    def _get_addressing_repository(self) -> AddressesRepository:
        """
        private method to get repository for providers
        """
        addressing_session = DbSession[AddressesRepository](engine=self.database.engine)
        return addressing_session.get_repository(Address)
