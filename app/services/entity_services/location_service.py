import logging
from datetime import datetime
from typing import Any, Sequence
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from fhir.resources.R4B.fhirtypes import Id
from fhir.resources.R4B.location import Location as FhirLocation

from app.db.db import Database
from app.db.entities.location.location import Location
from app.db.entities.organization.organization import Organization
from app.db.repositories.location_repository import LocationRepository
from app.db.repositories.organizations_repository import OrganizationsRepository
from app.db.session import DbSession
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.services.reference_validator import ReferenceValidator
from app.services.utils import split_reference


class LocationService:
    def __init__(self, database: Database):
        self.database = database

    def find(
        self,
        params: dict[str, Any],
    ) -> Sequence[Location]:
        with self.database.get_db_session() as session:
            params["latest"] = True

            repo = session.get_repository(LocationRepository)
            return repo.find(**params)

    def add_one(self, fhir_entity: FhirLocation) -> Location:
        with self.database.get_db_session() as session:
            repo = session.get_repository(LocationRepository)

            self._check_references(session, fhir_entity)

            fhir_entity.meta = None  # type: ignore
            id = uuid4()
            fhir_entity.id = Id(str(id))

            instance = Location(
                version=1,
                fhir_id=id,
                data=jsonable_encoder(fhir_entity.dict()),
            )
            return repo.create(instance)

    def delete_one(self, resource_id: UUID) -> None:
        with self.database.get_db_session() as session:
            repo = session.get_repository(LocationRepository)
            entity = repo.get_one(fhir_id=str(resource_id))

            if entity is None or entity.data is None:
                logging.warning(f"Location not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Location not found for {str(resource_id)}")

            repo.delete(entity)

    def get_one(self, resource_id: UUID) -> Location:
        with self.database.get_db_session() as session:
            repo = session.get_repository(LocationRepository)
            entity = repo.get_one(fhir_id=str(resource_id))

            if entity is None or entity.data is None:
                logging.warning(f"Location not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Location not found for {str(resource_id)}")

            return entity

    def get_one_version(self, resource_id: UUID, version_id: int) -> Location:
        with self.database.get_db_session() as session:
            repo = session.get_repository(LocationRepository)
            entity = repo.get(fhir_id=str(resource_id), version=version_id)

            if entity is None:
                logging.warning(f"Version not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Version not found for {str(resource_id)}")

            return entity

    def update_one(self, resource_id: UUID, fhir_entity: FhirLocation) -> Location:
        with self.database.get_db_session() as session:
            # Remove metadata, as it will be added by the repository
            fhir_entity.meta = None  # type: ignore

            repo = session.get_repository(LocationRepository)
            entity = repo.get_one(fhir_id=resource_id)

            if entity is None or entity.data is None:
                logging.warning(f"Location not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Location not found for {str(resource_id)}")

            self._check_references(session, fhir_entity)

            # Remove metadata temporary in order to compare the data
            meta = entity.data.pop("meta")
            if jsonable_encoder(entity.data) == jsonable_encoder(fhir_entity.dict()):
                entity.data["meta"] = meta
                return entity  # The old and the new are the same, no need to create a new version for this

            return repo.update(entity, fhir_entity.dict())

    def find_history(self, id: UUID | None = None, since: datetime | None = None) -> Sequence[Location]:
        params = {
            "latest": False,
            "sort_history": True,
            "id": id,
            "since": since,
        }

        with self.database.get_db_session() as session:
            repo = session.get_repository(LocationRepository)
            return repo.find(**params)

    @staticmethod
    def _check_references(session: DbSession, fhir_entity: FhirLocation) -> None:
        reference_validator = ReferenceValidator()

        if fhir_entity.managingOrganization is not None:
            reference_validator.validate_reference(session, fhir_entity.managingOrganization, match_on="Organization")

        if fhir_entity.partOf is not None:
            reference_validator.validate_reference(session, fhir_entity.partOf, match_on="Location")

    def get_organizations(self, entries: list[Location]) -> list[Organization]:
        """
        Fetches the organizations for the given locations
        """
        organization_entities = []

        with self.database.get_db_session() as session:
            repo = session.get_repository(OrganizationsRepository)

            for location in entries:
                if "managingOrganization" not in location.data:  # type: ignore
                    continue

                for organization in location.data["managingOrganization"]:  # type: ignore
                    (ref_type, ref_id) = split_reference(organization["reference"])

                    organization_entity = repo.get_one(fhir_id=ref_id)
                    if organization_entity is None:
                        logging.warning(f"Organization {ref_id} not found for {location.fhir_id}")
                        continue

                    organization_entities.append(organization_entity)

        return organization_entities
