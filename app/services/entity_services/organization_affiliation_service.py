import logging
from datetime import datetime
from typing import Any, Sequence
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from fhir.resources.R4B.fhirtypes import Id
from fhir.resources.R4B.organizationaffiliation import (
    OrganizationAffiliation as FhirOrganizationAffiliation,
)

from app.db.db import Database
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.entities.organization_affiliation.organization_affiliation import (
    OrganizationAffiliation,
)
from app.db.repositories.endpoints_repository import EndpointsRepository
from app.db.repositories.organization_affiliation_repository import (
    OrganizationAffiliationRepository,
)
from app.db.session import DbSession
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.services.reference_validator import ReferenceValidator
from app.services.utils import split_reference


class OrganizationAffiliationService:
    def __init__(self, database: Database):
        self.database = database

    def find(
        self,
        params: dict[str, Any],
    ) -> Sequence[OrganizationAffiliation]:
        with self.database.get_db_session() as session:
            params["latest"] = True

            repo = session.get_repository(OrganizationAffiliationRepository)
            return repo.find(**params)

    def add_one(self, fhir_entity: FhirOrganizationAffiliation) -> OrganizationAffiliation:
        with self.database.get_db_session() as session:
            repo = session.get_repository(OrganizationAffiliationRepository)

            self._check_references(session, fhir_entity)

            fhir_entity.meta = None  # type: ignore
            id = uuid4()
            fhir_entity.id = Id(str(id))

            instance = OrganizationAffiliation(
                version=1,
                fhir_id=id,
                data=jsonable_encoder(fhir_entity.dict()),
            )
            return repo.create(instance)

    def delete_one(self, resource_id: UUID) -> None:
        with self.database.get_db_session() as session:
            repo = session.get_repository(OrganizationAffiliationRepository)
            entity = repo.get_one(fhir_id=str(resource_id))

            if entity is None or entity.data is None:
                logging.warning(f"OrganizationAffiliation not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"OrganizationAffiliation not found for {str(resource_id)}")

            repo.delete(entity)

    def get_one(self, resource_id: UUID) -> OrganizationAffiliation:
        with self.database.get_db_session() as session:
            repo = session.get_repository(OrganizationAffiliationRepository)
            entity = repo.get_one(fhir_id=str(resource_id))

            if entity is None or entity.data is None:
                logging.warning(f"OrganizationAffiliation not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"OrganizationAffiliation not found for {str(resource_id)}")

            return entity

    def get_one_version(self, resource_id: UUID, version_id: int) -> OrganizationAffiliation:
        with self.database.get_db_session() as session:
            repo = session.get_repository(OrganizationAffiliationRepository)
            entity = repo.get(fhir_id=str(resource_id), version=version_id)

            if entity is None:
                logging.warning(f"Version not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Version not found for {str(resource_id)}")

            return entity

    def update_one(self, resource_id: UUID, fhir_entity: FhirOrganizationAffiliation) -> OrganizationAffiliation:
        with self.database.get_db_session() as session:
            # Remove metadata, as it will be added by the repository
            fhir_entity.meta = None  # type: ignore

            repo = session.get_repository(OrganizationAffiliationRepository)
            entity = repo.get_one(fhir_id=resource_id)

            if entity is None or entity.data is None:
                logging.warning(f"OrganizationAffiliation not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"OrganizationAffiliation not found for {str(resource_id)}")

            self._check_references(session, fhir_entity)

            # Remove metadata temporary in order to compare the data
            meta = entity.data.pop("meta")
            if jsonable_encoder(entity.data) == jsonable_encoder(fhir_entity.dict()):
                entity.data["meta"] = meta
                return entity  # The old and the new are the same, no need to create a new version for this

            return repo.update(entity, fhir_entity.dict())

    def find_history(self, id: UUID | None = None, since: datetime | None = None) -> Sequence[OrganizationAffiliation]:
        params = {
            "latest": False,
            "sort_history": True,
            "id": id,
            "since": since,
        }

        with self.database.get_db_session() as session:
            repo = session.get_repository(OrganizationAffiliationRepository)
            return repo.find(**params)

    @staticmethod
    def _check_references(session: DbSession, fhir_entity: FhirOrganizationAffiliation) -> None:
        reference_validator = ReferenceValidator()

        if fhir_entity.healthcareService is not None:
            reference_validator.validate_list(session, fhir_entity.healthcareService, match_on="HealthcareService")

        if fhir_entity.organization is not None:
            reference_validator.validate_reference(session, fhir_entity.organization, match_on="Organization")

        if fhir_entity.participatingOrganization is not None:
            reference_validator.validate_reference(
                session, fhir_entity.participatingOrganization, match_on="Organization"
            )
        if fhir_entity.network is not None and len(fhir_entity.network) > 0:
            reference_validator.validate_list(session, fhir_entity.network, match_on="Organization")

    def get_endpoints(self, entries: list[OrganizationAffiliation]) -> list[Endpoint]:
        """
        Fetches the endpoints for the given organization affiliations
        """
        endpoint_entities = []

        with self.database.get_db_session() as session:
            repo = session.get_repository(EndpointsRepository)

            for affiliation in entries:
                if "endpoint" not in affiliation.data:  # type: ignore
                    continue

                for endpoint in affiliation.data["endpoint"]:  # type: ignore
                    (ref_type, ref_id) = split_reference(endpoint["reference"])

                    endpoint_entity = repo.get_one(fhir_id=ref_id)
                    if endpoint_entity is None:
                        logging.warning(f"Endpoint {ref_id} not found for {affiliation.fhir_id}")
                        continue

                    endpoint_entities.append(endpoint_entity)

        return endpoint_entities
