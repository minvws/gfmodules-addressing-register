import logging
from uuid import UUID
from typing import List, Union

from sqlalchemy import select
from sqlalchemy.exc import DatabaseError

from app.db.decorator import repository
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.repositories.repository_base import RepositoryBase

logger = logging.getLogger(__name__)

class RepositoryException(Exception):
    pass

@repository(Endpoint)
class EndpointsRepository(RepositoryBase):
    def get(self, **kwargs: Union[str, UUID, dict[str, str]]) -> Endpoint | None:
        stmt = (
            select(Endpoint)
            .filter_by(**kwargs)
        )
        result = self.db_session.execute(stmt).scalars().first()
        if result is None or isinstance(result, Endpoint):
            return result
        raise TypeError("Result not of type Endpoint")

    def get_many(self, **kwargs: Union[str, UUID, dict[str, str]]) -> List[Endpoint]:
        stmt = select(Endpoint).filter_by(**kwargs)
        result = self.db_session.execute(stmt).scalars().all()
        if isinstance(result, List):
            return result
        raise TypeError("Result not of type List")

    def create(self, endpoint: Endpoint) -> Endpoint:
        try:
            self.db_session.add(endpoint)
            self.db_session.commit()
            return endpoint
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add Endpoint {endpoint}: {e}")
            raise RepositoryException(f"Failed to add Endpoint {endpoint}")

    def delete(self, endpoint: Endpoint) -> None:
        try:
            self.db_session.delete(endpoint)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to delete Endpoint {endpoint}: {e}")
            raise e

    def update(self, endpoint: Endpoint) -> Endpoint:
        try:
            self.db_session.add(endpoint)
            self.db_session.commit()
            return endpoint
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to update Endpoint {endpoint}: {e}")
            raise e
