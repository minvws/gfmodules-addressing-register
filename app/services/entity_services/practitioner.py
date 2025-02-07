import logging
from datetime import datetime
from typing import Any, Sequence
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from fhir.resources.R4B.practitioner import (
    Practitioner as FhirPractitioner,
)
from fhir.resources.R4B.practitioner import (
    PractitionerQualification,
)

from app.db.db import Database
from app.db.entities.practitioner.practitioner import Practitioner
from app.db.repositories.practitioners_repository import (
    PractitionerRepository,
)
from app.db.session import DbSession
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.services.reference_validator import ReferenceValidator


class PractitionerService:
    def __init__(self, database: Database):
        self.database = database

    def find(
        self,
        params: dict[str, Any],
    ) -> Sequence[Practitioner]:
        with self.database.get_db_session() as session:
            params["latest"] = True

            repo = session.get_repository(PractitionerRepository)
            return repo.find(**params)

    def add_one(self, fhir_entity: FhirPractitioner, id: UUID | None = None) -> Practitioner:
        with self.database.get_db_session() as session:
            repo = session.get_repository(PractitionerRepository)

            self._check_references(session, fhir_entity)

            fhir_entity.meta = None
            if id is None:
                id = uuid4()
            fhir_entity.id = str(id)

            instance = Practitioner(
                version=1,
                fhir_id=id,
                data=jsonable_encoder(fhir_entity.dict()),
            )
            return repo.create(instance)

    def delete_one(self, resource_id: UUID) -> None:
        with self.database.get_db_session() as session:
            repo = session.get_repository(PractitionerRepository)
            entity = repo.get_one(fhir_id=str(resource_id))

            if entity is None or entity.data is None:
                logging.warning(f"Practitioner not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Practitioner not found for {str(resource_id)}")

            repo.delete(entity)

    def get_one(self, resource_id: UUID) -> Practitioner:
        with self.database.get_db_session() as session:
            repo = session.get_repository(PractitionerRepository)
            entity = repo.get_one(fhir_id=str(resource_id))

            if entity is None or entity.data is None:
                logging.warning(f"Practitioner not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Practitioner not found for {str(resource_id)}")

            return entity

    def get_one_version(self, resource_id: UUID, version_id: int) -> Practitioner:
        with self.database.get_db_session() as session:
            repo = session.get_repository(PractitionerRepository)
            entity = repo.get(fhir_id=str(resource_id), version=version_id)

            if entity is None:
                logging.warning(f"Version not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Version not found for {str(resource_id)}")

            return entity

    def update_one(self, resource_id: UUID, fhir_entity: FhirPractitioner) -> Practitioner:
        with self.database.get_db_session() as session:
            # Remove metadata, as it will be added by the repository
            fhir_entity.meta = None

            repo = session.get_repository(PractitionerRepository)
            entity = repo.get_one(fhir_id=resource_id)

            if entity is None or entity.data is None:
                logging.warning(f"Practitioner not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Practitioner not found for {str(resource_id)}")

            self._check_references(session, fhir_entity)

            # Remove metadata temporary in order to compare the data
            meta = entity.data.pop("meta")
            if jsonable_encoder(entity.data) == jsonable_encoder(fhir_entity.dict()):
                entity.data["meta"] = meta
                return entity  # The old and the new are the same, no need to create a new version for this

            return repo.update(entity, fhir_entity.dict())

    def find_history(self, id: UUID | None = None, since: datetime | None = None) -> Sequence[Practitioner]:
        params = {
            "latest": False,
            "sort_history": True,
            "id": id,
            "since": since,
        }

        with self.database.get_db_session() as session:
            repo = session.get_repository(PractitionerRepository)
            return repo.find(**params)

    @staticmethod
    def _check_references(session: DbSession, fhir_entity: FhirPractitioner) -> None:
        reference_validator = ReferenceValidator()

        if fhir_entity.qualification is not None:
            for qualification in fhir_entity.qualification:
                if not isinstance(qualification, PractitionerQualification):
                    raise TypeError(f"Expected `PractitionerQualification` but received {type(qualification)}")
                if qualification.issuer is not None:
                    reference_validator.validate_reference(session, qualification.issuer, match_on="Organization")
