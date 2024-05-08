import logging
from typing import List, Sequence, TypeVar, Mapping, Dict

from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DatabaseError
from app.db.decorator import repository
from app.db.entities.address_entity import AddressEntity
from app.db.repositories.repository_base import RepositoryBase

logger = logging.getLogger(__name__)


TAddressDict = TypeVar(
    "TAddressDict", bound=Mapping[str, str | Mapping[str, str | List[str]]]
)


@repository(AddressEntity)
class AddressesRepository(RepositoryBase):
    def __init__(self, session: Session):
        super().__init__(session)

    def find_one(self, provider_id: str, data_domain: str) -> AddressEntity | None:
        """
        Find one addressing by provider_id and data_domain
        """
        stmt = (
            select(AddressEntity)
            .where(AddressEntity.provider_id == provider_id)
            .where(AddressEntity.data_domain == data_domain)
        )

        results = self.session.execute(stmt).scalars().first()

        return results

    def find_many(self, params: List[Dict[str, str]]) -> List[AddressEntity]:
        results = []
        for param in params:
            address = self.find_one(
                provider_id=param["provider_id"], data_domain=param["data_domain"]
            )

            if address is not None:
                results.append(address)

        return results

    def create_one(
        self,
        new_address: TAddressDict,
    ) -> AddressEntity | None:
        """
        Add one addressing to the database
        """
        stmt = (
            insert(AddressEntity)
            .values(**new_address)
            .on_conflict_do_nothing(
                index_elements=[AddressEntity.provider_id, AddressEntity.data_domain]
            )
            .returning(AddressEntity)
        )
        result = self.session.execute(stmt).scalars().first()

        self.session.commit()
        return result

    def create_many(
        self, new_addresses: List[TAddressDict]
    ) -> Sequence[AddressEntity] | None:
        """
        Create bulk addresses for multiple providers
        """
        try:
            results = self.session.scalars(
                insert(AddressEntity).returning(AddressEntity),
                new_addresses,
            ).all()
            self.session.commit()

            return results
        except DatabaseError:
            self.session.rollback()
            return None

    def delete_one(self, provider_id: str, data_domain: str) -> int:
        try:
            stmt = (
                delete(AddressEntity)
                .where(AddressEntity.provider_id == provider_id)
                .where(AddressEntity.data_domain == data_domain)
            )
            result = self.session.execute(stmt)
            self.session.commit()

            return result.rowcount
        except DatabaseError:
            self.session.rollback()
            return 0

    def delete_many(self, data: List[TAddressDict]) -> int:
        row_count = 0
        for item in data:
            try:
                stmt = (
                    delete(AddressEntity)
                    .where(AddressEntity.provider_id == item["provider_id"])
                    .where(AddressEntity.data_domain == item["data_domain"])
                )
                result = self.session.execute(stmt)
                row_count += result.rowcount
                self.session.commit()
            except DatabaseError:
                self.session.rollback()
                row_count = 0
                break

        return row_count
