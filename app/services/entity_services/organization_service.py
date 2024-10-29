import logging
from typing import List, Sequence
from uuid import UUID

from app.data import UraNumber
from app.db.db import Database
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.entities.organization.organization import Organization
from app.db.repositories.endpoints_repository import EndpointsRepository
from app.db.repositories.organizations_repository import OrganizationsRepository
from app.exceptions.service_exceptions import (
    ResourceNotAddedException,
    ResourceNotFoundException,
)
from app.models.organization.model import OrganizationModel
from app.services.entity_services.abstraction import EntityService
from app.services.organization_history_service import OrganizationHistoryService


class OrganizationService(EntityService):
    def __init__(self, database: Database, history_service: OrganizationHistoryService):
        super().__init__(database)
        self.history_service = history_service

    def find(
        self,
        id: UUID | None = None,
        ura_number: str | None = None,
        active: bool | None = None,
        name: str | None = None,
        type: str | None = None,
        parent_organization_id: UUID | None = None,
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

    def add_one(
        self, organization: OrganizationModel, endpoints: List[Endpoint] | None = None
    ) -> Organization:
        with self.database.get_db_session() as session:
            organization_repository = session.get_repository(OrganizationsRepository)
            try:
                if (
                    organization_repository.get(ura_number=str(organization.ura_number))
                    is not None
                ):
                    logging.error(
                        f"Failed to add organization {organization.ura_number}: Organization with URA number already exists"
                    )
                    raise ResourceNotAddedException()

                if organization.parent_organization_id is not None:
                    if (
                        organization_repository.get(
                            id=organization.parent_organization_id
                        )
                        is None
                    ):
                        logging.error(
                            f"Failed to add organization {organization.ura_number}: Parent organization {organization.parent_organization_id} does not exist"
                        )
                        raise ResourceNotFoundException("Parent organization not found")

                organization_entity = Organization(**organization.model_dump())
                if endpoints is not None:
                    organization_entity.endpoints = endpoints

                new_org = organization_repository.create(organization_entity)
                self.history_service.create(new_org, "create")
                return new_org
            except Exception as e:
                logging.error(f"Failed to add organization {organization}: {str(e)}")
                raise ResourceNotAddedException()

    def get_one(self, ura_number: UraNumber) -> Organization:
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
            if parent_organization_id is not None:
                if organization_repository.get(id=parent_organization_id) is None:
                    logging.error(
                        f"Failed to get organizations: Parent organization {parent_organization_id} does not exist"
                    )
                    raise ResourceNotFoundException("Parent organization not found")
            params = {
                "ura_number": ura_number,
                "name": name,
                "active": active,
                "description": description,
                "parent_organization_id": parent_organization_id,
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
        active: bool | None = None,
        name: str | None = None,
        description: str | None = None,
        parent_org: UUID | None = None,
        endpoints: List[Endpoint] | None = None,
    ) -> Organization:
        with self.database.get_db_session() as session:
            organization_repository = session.get_repository(OrganizationsRepository)
            endpoints_repository = session.get_repository(EndpointsRepository)
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
                if organization_repository.get(id=parent_org) is None:
                    logging.error(
                        f"Failed to update organization: Parent organization {parent_org} does not exist"
                    )
                    raise ResourceNotFoundException("Parent organization not found")
                entity.parent_organization_id = parent_org
            if endpoints is not None:
                target_endpoints = entity.endpoints
                entity.endpoints = endpoints
                endpoints_repository.delete_many(target_endpoints)

            updated_org = organization_repository.update(entity)
            self.history_service.create(updated_org, "update")
            return updated_org

    def delete_one(self, ura_number: UraNumber) -> None:
        with self.database.get_db_session() as session:
            organization_repository = session.get_repository(OrganizationsRepository)
            organization = organization_repository.get(ura_number=str(ura_number))
            if organization is None:
                logging.warning(f"Organization not found for {ura_number}")
                raise ResourceNotFoundException()
            organization_repository.delete(organization)
            self.history_service.create(organization, "delete")
