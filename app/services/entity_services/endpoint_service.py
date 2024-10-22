import logging
from datetime import datetime
from typing import Sequence
from uuid import UUID

from app.data import EndpointStatus, ConnectionType
from app.db.db import Database
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.entities.endpoint.endpoint_payload import EndpointPayload
from app.db.repositories.endpoint_payload_type_repository import EndpointPayloadTypeRepository
from app.db.repositories.endpoints_repository import EndpointsRepository
from app.db.repositories.organizations_repository import OrganizationsRepository
from app.db.repositories.repository_exception import RepositoryException
from app.exceptions.service_exceptions import (
    ResourceNotFoundException,
)
from app.services.entity_services.abstraction import EntityService
from app.services.organization_history_service import OrganizationHistoryService

class EndpointService(EntityService):

    def __init__(self, database: Database, organization_history_service: OrganizationHistoryService):
        super().__init__(database)
        self.organization_history_service = organization_history_service

    def find(
        self,
        id: UUID | None = None,
        identifier: UUID | None = None,
        organization_id: UUID | None = None,
        updated_at: datetime | None = None,
    ) -> Sequence[Endpoint]:
        params = {"id": id if id else identifier, "organization_id": organization_id}
        filtered_params = {k: v for k, v in params.items() if v is not None}

        with self.database.get_db_session() as session:
            endpoints_repository = session.get_repository(EndpointsRepository)
            return endpoints_repository.find(**filtered_params)

    def add_one(
        self,
        name: str | None,
        description: str | None,
        address: str,
        status_type: EndpointStatus,
        organization_id: UUID | None,
        connection_type: ConnectionType,
        payload_type: str,
        payload_mime_type: str,
    ) -> Endpoint:
        with self.database.get_db_session() as session:
            endpoint_repository = session.get_repository(EndpointsRepository)
            organization_repository = session.get_repository(OrganizationsRepository)
            organization = None
            new_endpoint = Endpoint(
                name=name,
                description=description,
                address=address,
                status_type=str(status_type),
                connection_type=str(connection_type),
            )
            if organization_id is not None:
                organization = organization_repository.get(id=organization_id)
                if organization is None:
                    raise ResourceNotFoundException(f"Organization {organization_id} was not found")
                new_endpoint.managing_organization = organization
            association = EndpointPayload(
                endpoint_id=new_endpoint.id,
                payload_type=payload_type,
                mime_type=payload_mime_type,
            )
            endpoint_payload_type_repository = session.get_repository(EndpointPayloadTypeRepository)
            try:
                association.payload = endpoint_payload_type_repository.get(code=payload_type)
            except RepositoryException:
                raise ResourceNotFoundException(f"Payload type {payload_type} was not found")
            new_endpoint.payload.append(association)
            created_endpoint = endpoint_repository.create(new_endpoint)
            if organization is not None:
                self.organization_history_service.create(organization=organization, interaction="update")
            return created_endpoint

    def delete_one(self, endpoint_id: UUID) -> None:
        with self.database.get_db_session() as session:
            endpoint_repository = session.get_repository(EndpointsRepository)
            organization_repository = session.get_repository(OrganizationsRepository)
            organization = None
            endpoint = endpoint_repository.get(id=endpoint_id)
            if endpoint is None:
                logging.warning("Endpoint not found for %s", endpoint_id)
                raise ResourceNotFoundException()
            if endpoint.organization_id is not None:
                organization = organization_repository.get(id=endpoint.organization_id)
                if organization is None:
                    raise ResourceNotFoundException(f"Organization {endpoint.organization_id} was not found")
            endpoint_repository.delete(endpoint)
            if organization is not None:
                self.organization_history_service.create(organization=organization, interaction="update")

    def get_one(self, endpoint_id: UUID) -> Endpoint:
        with self.database.get_db_session() as session:
            endpoint_repository = session.get_repository(EndpointsRepository)
            endpoint = endpoint_repository.get(id=endpoint_id)
            if endpoint is None:
                logging.warning("Endpoint not found for %s", endpoint_id)
                raise ResourceNotFoundException()
            return endpoint

    def get_many(
        self,
        name: str | None = None,
        description: str | None = None,
        address: str | None = None,
        status_type: EndpointStatus | None = None,
        organization_id: UUID | None = None,
    ) -> Sequence[Endpoint]:
        with self.database.get_db_session() as session:
            endpoint_repository = session.get_repository(EndpointsRepository)
            organization_repository = session.get_repository(OrganizationsRepository)
            if organization_id is not None:
                if organization_repository.get(id=organization_id) is None:
                    raise ResourceNotFoundException(f"Organization {organization_id} was not found")
            params = {
                "name": name,
                "description": description,
                "address": address,
                "status_type": str(status_type) if status_type is not None else None,
                "organization_id": organization_id,
            }
            # Remove keys with None values
            filtered_params = {k: v for k, v in params.items() if v is not None}
            entities = endpoint_repository.get_many(**filtered_params)
            if len(entities) == 0:
                logging.warning("No endpoints found")
                raise ResourceNotFoundException()
            return entities

    def update_one(
        self,
        endpoint_id: UUID,
        name: str | None,
        description: str | None,
        address: str | None,
        status_type: EndpointStatus | None,
        organization_id: UUID | None,
    ) -> Endpoint:
        with self.database.get_db_session() as session:
            endpoint_repository = session.get_repository(EndpointsRepository)
            organization_repository = session.get_repository(OrganizationsRepository)
            organization = None
            update_endpoint = endpoint_repository.get(id=endpoint_id)
            if update_endpoint is None:
                logging.warning("Endpoint not found for %s", endpoint_id)
                raise ResourceNotFoundException()

            if address is not None:
                update_endpoint.address = address
            if description is not None:
                update_endpoint.description = description
            if status_type is not None:
                update_endpoint.status_type = str(status_type)
            if name is not None:
                update_endpoint.name = name
            if organization_id is not None:
                organization = organization_repository.get(id=organization_id)
                if organization is None:
                    logging.warning("Organization %s was not found", organization_id)
                    raise ResourceNotFoundException(f"Organization {organization_id} was not found")
                update_endpoint.managing_organization = organization
            updated_endpoint = endpoint_repository.update(update_endpoint)
            if organization is not None:
                self.organization_history_service.create(organization=organization, interaction="update")
            return updated_endpoint
