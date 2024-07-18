import logging
from typing import List

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DatabaseError

from app.data import UraNumber, DataDomain
from app.db.decorator import repository
from app.db.entities.address_entity import AddressEntity
from app.db.repositories.repository_base import RepositoryBase
from app.models.address.dto import AddressRequest
from app.models.address.model import Address

logger = logging.getLogger(__name__)


class RepositoryException(Exception):
    pass


@repository(AddressEntity)
class AddressesRepository(RepositoryBase):
    def find_one(self, ura_number: UraNumber, data_domain: DataDomain) -> AddressEntity | None:
        """
        Find one addressing by ura_number and data_domain
        """
        stmt = (
            select(AddressEntity)
            .where(AddressEntity.ura_number == str(ura_number))
            .where(AddressEntity.data_domain == str(data_domain))
        )

        return self.db_session.execute(stmt).scalars().first()  # type: ignore

    def find_many(self, params: List[AddressRequest]) -> List[AddressEntity]:
        results = []
        for base in params:
            address = self.find_one(ura_number=base.ura_number, data_domain=base.data_domain)
            if address is not None:
                results.append(address)

        return results

    def create_one(self, address: Address) -> None:
        """
        Add one addressing to the database
        """
        stmt = (
            insert(AddressEntity)
            .values(**address.model_dump())
            .on_conflict_do_nothing(
                index_elements=[AddressEntity.ura_number, AddressEntity.data_domain]
            )
            .returning(AddressEntity)
        )
        try:
            self.db_session.execute(stmt).scalars().first()
            self.db_session.commit()
        except DatabaseError as e:
            logging.error(f"Failed to add address {address}: {e}")
            raise RepositoryException(f"Failed to add address {address}")

    def create_many(self, addresses: List[Address]) -> None:
        """
        Create bulk addresses for multiple providers
        """
        entities = []
        for address in addresses:
            entities.append(address.model_dump())

        try:
            self.db_session.session.scalars(
                insert(AddressEntity).returning(AddressEntity),
                entities
            ).all()
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add addresses {addresses}: {e}")
            raise RepositoryException(f"Failed to add addresses {addresses}")

    def delete_one(self, ura_number: UraNumber, data_domain: DataDomain) -> int:
        try:
            stmt = (
                delete(AddressEntity)
                .where(AddressEntity.ura_number == str(ura_number))
                .where(AddressEntity.data_domain == str(data_domain))
            )
            result = self.db_session.execute(stmt)
            self.db_session.commit()

            return result.rowcount  # type: ignore
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to delete address {ura_number} {data_domain}: {e}")
            return 0

    def delete_many(self, data: List[AddressRequest]) -> int:
        row_count = 0
        for address_request in data:
            ura_number = str(address_request.ura_number)
            data_domain = str(address_request.data_domain)

            try:
                stmt = (
                    delete(AddressEntity)
                    .where(AddressEntity.ura_number == ura_number)
                    .where(AddressEntity.data_domain == data_domain)
                )
                result = self.db_session.execute(stmt)
                row_count += result.rowcount
                self.db_session.commit()
            except DatabaseError as e:
                self.db_session.rollback()
                logging.error(f"Failed to delete address {ura_number} {data_domain}: {e}")
                row_count = 0
                break

        return row_count
