import logging
from datetime import datetime
from typing import Any, Sequence
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from fhir.resources.R4B.practitionerrole import (
    PractitionerRole as FhirPractitionerRole,
)

from app.db.db import Database
from app.db.entities.practitioner.practitioner import Practitioner
from app.db.entities.practitioner_role.practitioner_role import (
    PractitionerRole,
)
from app.db.repositories.practitioner_role_repository import (
    PractitionerRoleRepository,
)
from app.db.repositories.practitioners_repository import PractitionerRepository
from app.db.session import DbSession
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.services.reference_validator import ReferenceValidator
from app.services.utils import split_reference


class PractitionerRoleService:
    def __init__(self, database: Database):
        self.database = database

    def find(
        self,
        params: dict[str, Any],
    ) -> Sequence[PractitionerRole]:
        with self.database.get_db_session() as session:
            params["latest"] = True

            repo = session.get_repository(PractitionerRoleRepository)
            return repo.find(**params)

    def add_one(self, fhir_entity: FhirPractitionerRole) -> PractitionerRole:
        with self.database.get_db_session() as session:
            repo = session.get_repository(PractitionerRoleRepository)

            self._check_references(session, fhir_entity)

            fhir_entity.meta = None
            id = uuid4()
            fhir_entity.id = str(id)

            instance = PractitionerRole(
                version=1,
                fhir_id=id,
                data=jsonable_encoder(fhir_entity.dict()),
            )
            return repo.create(instance)

    def delete_one(self, resource_id: UUID) -> None:
        with self.database.get_db_session() as session:
            repo = session.get_repository(PractitionerRoleRepository)
            entity = repo.get_one(fhir_id=str(resource_id))

            if entity is None or entity.data is None:
                logging.warning(f"PractitionerRole not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"PractitionerRole not found for {str(resource_id)}")

            repo.delete(entity)

    def get_one(self, resource_id: UUID) -> PractitionerRole:
        with self.database.get_db_session() as session:
            repo = session.get_repository(PractitionerRoleRepository)
            entity = repo.get_one(fhir_id=str(resource_id))

            if entity is None or entity.data is None:
                logging.warning(f"PractitionerRole not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"PractitionerRole not found for {str(resource_id)}")

            return entity

    def get_one_version(self, resource_id: UUID, version_id: int) -> PractitionerRole:
        with self.database.get_db_session() as session:
            repo = session.get_repository(PractitionerRoleRepository)
            entity = repo.get(fhir_id=str(resource_id), version=version_id)

            if entity is None:
                logging.warning(f"Version not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Version not found for {str(resource_id)}")

            return entity

    def update_one(self, resource_id: UUID, fhir_entity: FhirPractitionerRole) -> PractitionerRole:
        with self.database.get_db_session() as session:
            # Remove metadata, as it will be added by the repository
            fhir_entity.meta = None

            repo = session.get_repository(PractitionerRoleRepository)
            entity = repo.get_one(fhir_id=resource_id)

            if entity is None or entity.data is None:
                logging.warning(f"PractitionerRole not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"PractitionerRole not found for {str(resource_id)}")

            self._check_references(session, fhir_entity)

            # Remove metadata temporary in order to compare the data
            meta = entity.data.pop("meta")
            if jsonable_encoder(entity.data) == jsonable_encoder(fhir_entity.dict()):
                entity.data["meta"] = meta
                return entity  # The old and the new are the same, no need to create a new version for this

            return repo.update(entity, fhir_entity.dict())

    def find_history(self, id: UUID | None = None, since: datetime | None = None) -> Sequence[PractitionerRole]:
        params = {
            "latest": False,
            "sort_history": True,
            "id": id,
            "since": since,
        }

        with self.database.get_db_session() as session:
            repo = session.get_repository(PractitionerRoleRepository)
            return repo.find(**params)

    @staticmethod
    def _check_references(session: DbSession, fhir_entity: FhirPractitionerRole) -> None:
        reference_validator = ReferenceValidator()

        if fhir_entity.practitioner is not None:
            reference_validator.validate_reference(session, fhir_entity.practitioner, match_on="Practitioner")

        if fhir_entity.organization is not None:
            reference_validator.validate_reference(session, fhir_entity.organization, match_on="Organization")

        if fhir_entity.location is not None:
            reference_validator.validate_list(session, fhir_entity.location, match_on="Location")

        if fhir_entity.healthcareService is not None:
            reference_validator.validate_list(session, fhir_entity.healthcareService, match_on="HealthcareService")

    def get_practitioners(self, entries: list[PractitionerRole]) -> list[Practitioner]:
        """
        Fetches the practitioners for the given roles
        """
        practitioner_entities = []

        with self.database.get_db_session() as session:
            repo = session.get_repository(PractitionerRepository)

            for role in entries:
                if "practitioner" not in role.data:  # type: ignore
                    continue

                for practitioner in role.data["practitioner"]:  # type: ignore
                    (ref_type, ref_id) = split_reference(practitioner["reference"])

                    practitioner_entity = repo.get_one(fhir_id=ref_id)
                    if practitioner_entity is None:
                        logging.warning(f"Practitioner {ref_id} not found for {role.fhir_id}")
                        continue

                    practitioner_entities.append(practitioner_entity)

        return practitioner_entities
