import logging
from typing import List
from uuid import UUID

from app.data import EndpointStatus
from app.db.db import Database
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.repositories.endpoints_repository import EndpointsRepository
from app.exceptions.service_exceptions import ResourceNotAddedException, ResourceNotFoundException

logger = logging.getLogger(__name__)

class EndpointService:
    def __init__(self, database: Database):
        self.database = database

    def add_one(self, name: str|None, description: str|None, address: str, status_type: EndpointStatus, organization_id: UUID|None) -> None:
        with self.database.get_db_session() as session:
            endpoint_repository = session.get_repository(EndpointsRepository)
            try:
                endpoint_entity = Endpoint(
                    name=name,
                    description=description,
                    address=address,
                    status_type=str(status_type),
                    organization_id=organization_id,
                )
                endpoint_repository.create(endpoint_entity)
            except Exception as e:
                logging.error(f"Failed to add endpoint: {str(e)}")
                raise ResourceNotAddedException()

    def delete_one(self, endpoint_id: UUID) -> None:
        with self.database.get_db_session() as session:
            endpoint_repository = session.get_repository(EndpointsRepository)
            endpoint = endpoint_repository.get(id=endpoint_id)
            if endpoint is None:
                logging.warning(f"Endpoint not found for {endpoint_id}")
                raise ResourceNotFoundException()
            endpoint_repository.delete(endpoint)

    def get_one(self, endpoint_id: UUID) -> Endpoint:
        with self.database.get_db_session() as session:
            endpoint_repository = session.get_repository(EndpointsRepository)
            endpoint = endpoint_repository.get(id=endpoint_id)
            if endpoint is None:
                logging.warning(f"Endpoint not found for {endpoint_id}")
                raise ResourceNotFoundException()
            return endpoint

    def get_many(self, name: str|None, description: str|None, address: str|None, status_type: EndpointStatus|None, organization_id: UUID|None) -> List[Endpoint]:
        with self.database.get_db_session() as session:
            endpoint_repository = session.get_repository(EndpointsRepository)
            params = {
                "name": name,
                "description": description,
                "address": address,
                "status_type": str(status_type) if status_type is not None else None,
                "organization_id": organization_id
            }
            # Remove keys with None values
            filtered_params = {k: v for k, v in params.items() if v is not None}
            entities = endpoint_repository.get_many(**filtered_params)
            if len(entities) == 0:
                logging.warning("No endpoints found")
                raise ResourceNotFoundException()
            return entities

    def update_endpoint(self, endpoint_id: UUID, name: str|None, description: str|None, address: str|None, status_type: EndpointStatus|None, organization_id: UUID|None) -> Endpoint:
        with self.database.get_db_session() as session:
            endpoint_repository = session.get_repository(EndpointsRepository)
            entity = endpoint_repository.get(id=endpoint_id)
            if entity is None:
                logging.warning(f"Endpoint not found for {endpoint_id}")
                raise ResourceNotFoundException()

            if address is not None:
                entity.address = address
            if description is not None:
                entity.description = description
            if status_type is not None:
                entity.status_type = str(status_type)
            if name is not None:
                entity.name = name
            if organization_id is not None:
                entity.organization_id = organization_id
            return endpoint_repository.update(entity)