import logging

from sqlalchemy import select
from sqlalchemy.exc import DatabaseError

from app.db.decorator import repository
from app.db.entities.supplier_endpoint import SupplierEndpoint
from app.db.repositories.repository_base import RepositoryBase
from app.db.repositories.repository_exception import RepositoryException

logger = logging.getLogger(__name__)


@repository(SupplierEndpoint)
class SuppliersRepository(RepositoryBase):
    def get(self, ura_number: str) -> SupplierEndpoint | None:
        try:
            stmt = select(SupplierEndpoint).where(
                SupplierEndpoint.ura_number == ura_number
            )
            supplier_entity = self.db_session.execute(stmt).scalars().first()
            if supplier_entity is None or isinstance(supplier_entity, SupplierEndpoint):
                return supplier_entity
            raise TypeError("Result not of type SupplierEndpoint")
        except DatabaseError as e:
            logging.error(f"Failed to get SupplierEndpoint {e}")
            raise RepositoryException(f"Failed to get SupplierEndpoint {e}")

    def create(self, supplier_entity: SupplierEndpoint) -> SupplierEndpoint:
        try:
            self.db_session.add(supplier_entity)
            self.db_session.commit()
            return supplier_entity
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add SupplierEndpoint: {e}")
            raise RepositoryException(f"Failed to add SupplierEndpoint: {e}")

    def update(self, supplier_entity: SupplierEndpoint) -> SupplierEndpoint:
        try:
            self.db_session.add(supplier_entity)
            self.db_session.commit()
            return supplier_entity
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to update SupplierEndpoint: {e}")
            raise RepositoryException(f"Failed to update SupplierEndpoint: {e}")

    def delete(self, supplier_entity: SupplierEndpoint) -> None:
        try:
            self.db_session.delete(supplier_entity)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to delete SupplierEndpoint: {e}")
            raise RepositoryException(f"Failed to delete SupplierEndpoint: {e}")
