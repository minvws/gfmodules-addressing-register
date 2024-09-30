import logging
from datetime import datetime
from typing import Optional, Sequence


from app.data import UraNumber
from app.db.db import Database
from uuid import UUID
from app.db.entities.organization.organization import Organization
from app.db.repositories.organizations_repository import OrganizationsRepository
from app.exceptions.service_exceptions import (
    ResourceNotAddedException,
    ResourceNotFoundException,
)
from app.models.organization.model import OrganizationModel

logger = logging.getLogger(__name__)


class OrganizationService:
    def __init__(self, database: Database):
        self.database = database

    def find(
        self,
        id: UUID | None = None,
        ura_number: str | None = None,
        active: bool | None = None,
        name: str | None = None,
        type: str | None = None,
        parent_organization_id: UUID | None = None,
        updated_at: datetime | None = None,
    ) -> Sequence[Organization]:
        params = {
            "id": id,
            "ura_number": ura_number,
            "active": active,
            "name": name,
            "type": type,
            "parent_organization_id": parent_organization_id,
        }
        filtered_params = {k: v for k, v in params.items() if v is not None}
        with self.database.get_db_session() as session:
            organization_repository = session.get_repository(OrganizationsRepository)
            return organization_repository.find(**filtered_params)

    def add_one(self, organization: OrganizationModel) -> Organization:
        with self.database.get_db_session() as session:
            organization_repository = session.get_repository(OrganizationsRepository)
            try:
                if (
                    organization_repository.get(ura_number=str(organization.ura_number))
                    is not None
                ):
                    logging.error(
                        f"Failed to add organization {organization}: Organization with URA number already exists"
                    )
                    raise ResourceNotAddedException()
                organization_entity = Organization(
                    ura_number=str(organization.ura_number),
                    active=organization.active,
                    name=organization.name,
                    description=organization.description,
                    parent_organization_id=organization.parent_organization_id,
                )
                return organization_repository.create(organization_entity)
            except Exception as e:
                logging.error(f"Failed to add organization {organization}: {str(e)}")
                raise ResourceNotAddedException()

    def get_one_by_ura(self, ura_number: UraNumber) -> Organization:
        with self.database.get_db_session() as session:
            organization_repository = session.get_repository(OrganizationsRepository)
            entity = organization_repository.get(ura_number=str(ura_number))
            if entity is None:
                logging.warning(f"Organization not found for {ura_number}")
                raise ResourceNotFoundException()
            return entity

    def get_many(
        self,
        ura_number: str | None = None,
        active: bool | None = None,
        name: str | None = None,
        description: str | None = None,
        parent_organization_id: UUID | None = None,
    ) -> Sequence[Organization]:
        with self.database.get_db_session() as session:
            organization_repository = session.get_repository(OrganizationsRepository)
            params = {
                "ura_number": ura_number,
                "name": name,
                "active": active,
                "description": description,
                "parent_organization_id": (
                    str(parent_organization_id)
                    if parent_organization_id is not None
                    else None
                ),
            }
            # Remove keys with None values
            filtered_params = {k: v for k, v in params.items() if v is not None}
            entities = organization_repository.get_many(**filtered_params)
            if len(entities) == 0:
                logging.warning("Organization not found")
                raise ResourceNotFoundException()
            return entities

    def update_one(
        self,
        ura_number: UraNumber,
        active: Optional[bool],
        name: str | None,
        description: str | None,
        parent_org: UUID | None,
    ) -> Organization:
        with self.database.get_db_session() as session:
            organization_repository = session.get_repository(OrganizationsRepository)
            entity = organization_repository.get(ura_number=str(ura_number))
            if entity is None:
                logging.warning(f"Organization not found for {ura_number}")
                raise ResourceNotFoundException()

            if active is not None:
                entity.active = active
            if name is not None:
                entity.name = name
            if description is not None:
                entity.description = description
            if parent_org is not None:
                entity.parent_organization_id = parent_org
            return organization_repository.update(entity)

    def delete_one(self, ura_number: UraNumber) -> None:
        with self.database.get_db_session() as session:
            organization_repository = session.get_repository(OrganizationsRepository)
            organization = organization_repository.get(ura_number=str(ura_number))
            if organization is None:
                logging.warning(f"Organization not found for {ura_number}")
                raise ResourceNotFoundException()
            organization_repository.delete(organization)
