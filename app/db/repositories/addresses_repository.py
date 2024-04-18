from typing import List, Dict
from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from app.db.decorator import repository
from app.db.models.address import Address
from app.db.repositories.repository_base import RepositoryBase


@repository(Address)
class AddressesRepository(RepositoryBase):
    def __init__(self, session: Session):
        super().__init__(session)

    def find_one_address(self, provider_id: str, data_domain: str) -> Address | None:
        """
        Find one addressing by provider_id and data_domain

        :param provider_id: Provider Indetifier
        :param data_domain: provider data domain requested (eg. beeldbank)
        :return: Tuple with total number of items and a list of examples
        """
        stmt = (
            select(Address)
            .where(Address.provider_id == provider_id)
            .where(Address.data_domain == data_domain)
        )
        results = self.session.execute(stmt).scalars().first()

        return results

    def add_one_address(
        self,
        provider_id: str,
        data_domain: str,
        endpoint: str,
        request_type: str,
        parameters: List[Dict[str, str]],
    ) -> None:
        """
        Add one addressing to the database
        """
        stmt = insert(Address).values(
            endpoint=endpoint,
            provider_id=provider_id,
            data_domain=data_domain,
            request_type=request_type,
            parameters=parameters,
        )
        self.session.execute(stmt)
        self.session.commit()
