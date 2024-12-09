import logging
from typing import Any, Sequence
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from fhir.resources.R4B.fhirtypes import Id
from fhir.resources.R4B.healthcareservice import (
    HealthcareService as FhirHealthcareService,
)

from app.db.db import Database
from app.db.entities.healthcare_service.healthcare_service import HealthcareService
from app.db.repositories.healthcare_service_repository import (
    HealthcareServiceRepository,
)
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.services.entity_services.abstraction import EntityService


class HealthcareServiceService(EntityService):
    def __init__(self, database: Database):
        super().__init__(database)

    def find(
        self,
        params: dict[str, Any],
    ) -> Sequence[HealthcareService]:
        with self.database.get_db_session() as session:
            params["latest"] = True

            repo = session.get_repository(HealthcareServiceRepository)
            return repo.find(**params)

    def add_one(
        self, fhir_entity: FhirHealthcareService, id: UUID | None = None
    ) -> HealthcareService:
        with self.database.get_db_session() as session:
            repo = session.get_repository(HealthcareServiceRepository)

            fhir_entity.meta = None  # type: ignore
            if id is None:
                id = uuid4()
            fhir_entity.id = Id(str(id))

            instance = HealthcareService(
                version=1,
                fhir_id=id,
                data=jsonable_encoder(fhir_entity.dict()),
            )
            return repo.create(instance)

    def delete_one(self, resource_id: UUID) -> None:
        with self.database.get_db_session() as session:
            repo = session.get_repository(HealthcareServiceRepository)
            entity = repo.get_one(fhir_id=str(resource_id))

            if entity is None or entity.data is None:
                logging.warning(f"HealthcareService not found for {str(resource_id)}")
                raise ResourceNotFoundException(
                    f"HealthcareService not found for {str(resource_id)}"
                )

            repo.delete(entity)

    def get_one(self, resource_id: UUID) -> HealthcareService:
        with self.database.get_db_session() as session:
            repo = session.get_repository(HealthcareServiceRepository)
            entity = repo.get_one(fhir_id=str(resource_id))

            if entity is None or entity.data is None:
                logging.warning(f"HealthcareService not found for {str(resource_id)}")
                raise ResourceNotFoundException(
                    f"HealthcareService not found for {str(resource_id)}"
                )

            return entity

    def get_one_version(self, resource_id: UUID, version_id: int) -> HealthcareService:
        with self.database.get_db_session() as session:
            repo = session.get_repository(HealthcareServiceRepository)
            entity = repo.get(fhir_id=str(resource_id), version=version_id)

            if entity is None:
                logging.warning(f"Version not found for {str(resource_id)}")
                raise ResourceNotFoundException(
                    f"Version not found for {str(resource_id)}"
                )

            return entity

    def update_one(
        self, resource_id: UUID, fhir_entity: FhirHealthcareService
    ) -> HealthcareService:
        with self.database.get_db_session() as session:
            # Remove metadata, as it will be added by the repository
            fhir_entity.meta = None  # type: ignore

            repo = session.get_repository(HealthcareServiceRepository)
            entity = repo.get_one(fhir_id=resource_id)

            if entity is None or entity.data is None:
                logging.warning(f"HealthcareService not found for {str(resource_id)}")
                raise ResourceNotFoundException(
                    f"HealthcareService not found for {str(resource_id)}"
                )

            # Remove metadata temporary in order to compare the data
            meta = entity.data.pop("meta")
            if jsonable_encoder(entity.data) == jsonable_encoder(fhir_entity.dict()):
                entity.data["meta"] = meta
                return entity  # The old and the new are the same, no need to create a new version for this

            return repo.update(entity, fhir_entity.dict())

    def find_history(self, id: UUID | None = None) -> Sequence[HealthcareService]:
        params = {
            "latest": False,
            "sort_history": True,
            "id": id,
        }

        with self.database.get_db_session() as session:
            repo = session.get_repository(HealthcareServiceRepository)
            return repo.find(**params)
