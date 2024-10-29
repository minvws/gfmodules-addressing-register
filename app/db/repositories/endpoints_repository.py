import logging
from typing import Sequence, Union, Any
from uuid import UUID

from sqlalchemy import select, delete, or_
from sqlalchemy.exc import DatabaseError

from app.db.decorator import repository
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.repositories.repository_base import RepositoryBase

logger = logging.getLogger(__name__)


@repository(Endpoint)
class EndpointsRepository(RepositoryBase):
    def get(self, **kwargs: Union[str, UUID, dict[str, str]]) -> Endpoint | None:
        stmt = select(Endpoint).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().first()

    def get_many(
        self, **kwargs: Union[str, UUID, dict[str, str]]
    ) -> Sequence[Endpoint]:
        stmt = select(Endpoint).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().all()

    def find(
        self, **conditions: Union[bool, str, UUID, dict[str, Any]]
    ) -> Sequence[Endpoint]:
        stmt = select(Endpoint)
        filter_conditions = []
        if "id" in conditions:
            filter_conditions.append(Endpoint.id == conditions["id"])

        if "identifier" in conditions:
            filter_conditions.append(Endpoint.identifier == conditions["identifier"])

        if "organization_id" in conditions:
            filter_conditions.append(
                Endpoint.organization_id == conditions["organization_id"]
            )

        stmt = stmt.where(*filter_conditions)
        return self.db_session.session.execute(stmt).scalars().all()

    def create(self, endpoint: Endpoint) -> Endpoint:
        try:
            self.db_session.add(endpoint)
            self.db_session.commit()
            return endpoint
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add Endpoint {endpoint.id}: {e}")
            raise e

    def delete(self, endpoint: Endpoint) -> None:
        try:
            self.db_session.delete(endpoint)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to delete Endpoint {endpoint.id}: {e}")
            raise e

    def update(self, endpoint: Endpoint) -> Endpoint:
        try:
            self.db_session.add(endpoint)
            self.db_session.commit()
            return endpoint
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to update Endpoint {endpoint.id}: {e}")
            raise e

    def delete_many(self, endpoints: Sequence[Endpoint]) -> None:
        stmt = delete(Endpoint).where(or_(*[Endpoint.id == endpoint.id for endpoint in endpoints]))
        self.db_session.execute(stmt)
