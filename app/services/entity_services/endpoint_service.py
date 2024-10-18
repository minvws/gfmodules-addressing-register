import logging
from datetime import datetime
from typing import Sequence
from uuid import UUID

from app.data import EndpointStatus, ConnectionType
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.repositories.endpoints_repository import EndpointsRepository
from app.db.repositories.organizations_repository import OrganizationsRepository
from app.exceptions.service_exceptions import (
    ResourceNotAddedException,
    ResourceNotFoundException,
)
from app.services.entity_services.abstraction import EntityService


class EndpointService(EntityService):

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
    ) -> Endpoint:
        with self.database.get_db_session() as session:
            endpoint_repository = session.get_repository(EndpointsRepository)
            organization_repository = session.get_repository(OrganizationsRepository)
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
                    logging.warning("Organization %s was not found", organization_id)
                    raise ResourceNotFoundException(f"Organization {organization_id} was not found")
                new_endpoint.managing_organization = organization
            try:
                return endpoint_repository.create(new_endpoint)
            except Exception as e:
                logging.error("Failed to add endpoint: %s", str(e))
                raise ResourceNotAddedException() from e

    def delete_one(self, endpoint_id: UUID) -> None:
        with self.database.get_db_session() as session:
            endpoint_repository = session.get_repository(EndpointsRepository)
            endpoint = endpoint_repository.get(id=endpoint_id)
            if endpoint is None:
                logging.warning("Endpoint not found for %s", endpoint_id)
                raise ResourceNotFoundException()
            endpoint_repository.delete(endpoint)

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
            return endpoint_repository.update(update_endpoint)
