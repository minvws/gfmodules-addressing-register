import logging
from typing import Union, Sequence, Any

from sqlalchemy import select, or_
from sqlalchemy.exc import DatabaseError
from uuid import UUID


from app.db.decorator import repository
from app.db.entities.organization.organization import Organization
from app.db.entities.organization.organization_type_association import (
    OrganizationTypeAssociation,
)
from app.db.repositories.repository_base import RepositoryBase

logger = logging.getLogger(__name__)


class RepositoryException(Exception):
    pass


@repository(Organization)
class OrganizationsRepository(RepositoryBase):
    def get(self, **kwargs: Union[str, UUID, dict[str, str]]) -> Organization | None:
        stmt = select(Organization).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().first()

    def get_many(
        self, **kwargs: Union[bool, str, UUID, dict[str, str]]
    ) -> Sequence[Organization]:
        stmt = select(Organization).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().all()

    def find(
        self, **conditions: Union[bool, str, UUID, dict[str, Any]]
    ) -> Sequence[Organization]:
        stmt = select(Organization)
        filter_conditions = []
        if "id" in conditions:
            filter_conditions.append(Organization.id == conditions["id"])

        if "parent_organization_id" in conditions:
            filter_conditions.append(
                Organization.parent_organization_id
                == conditions["parent_organization_id"]
            )

        if "name" in conditions:
            filter_conditions.append(Organization.name.ilike(f"%{conditions['name']}%"))

        if "active" in conditions:
            filter_conditions.append(Organization.active == conditions["active"])

        if "ura_number" in conditions:
            filter_conditions.append(
                Organization.ura_number == conditions["ura_number"]
            )

        if "type" in conditions:
            stmt = stmt.join(OrganizationTypeAssociation,
                             Organization.id == OrganizationTypeAssociation.organization_id)
            stmt = stmt.filter(OrganizationTypeAssociation.organization_type == conditions["type"])

        stmt = stmt.where(or_(*filter_conditions))
        return self.db_session.session.execute(stmt).scalars().all()

    def create(self, organization: Organization) -> Organization:
        try:
            self.db_session.add(organization)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add organization {organization}: {e}")
            raise RepositoryException(f"Failed to add organization {organization}")
        return organization

    def delete(self, organization: Organization) -> None:
        try:
            self.db_session.delete(organization)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to delete organization {organization}: {e}")
            raise e

    def update(self, organization: Organization) -> Organization:
        try:
            self.db_session.add(organization)
            self.db_session.commit()
            return organization
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to update organization {organization}: {e}")
            raise e
