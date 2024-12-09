from typing import Any, Dict
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.organizationaffiliation import OrganizationAffiliation

from app.db.db import Database
from app.db.repositories.organization_affiliation_repository import OrganizationAffiliationRepository
from app.db.entities.organization_affiliation.organization_affiliation import OrganizationAffiliationEntry
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.mappers.fhir_mapper import create_fhir_bundle
from app.db.repositories.endpoints_repository import EndpointsRepository
from app.params.organization_affiliation_query_params import OrganizationAffiliationQueryParams
from app.services.reference_validator import ReferenceValidator


class OrganizationAffiliationService:
    def __init__(self, database: Database):
        self.database = database

    def add_one(self, data: OrganizationAffiliation) -> OrganizationAffiliationEntry:
        with self.database.get_db_session() as session:
            repository = session.get_repository(OrganizationAffiliationRepository)

            reference_validator = ReferenceValidator()
            reference_validator.validate_list(session, data.healthcareService, match_on="HealthcareService")

            # @todo: check if organisation / participating / primary are in the db

            affiliation_entity = OrganizationAffiliationEntry(
                data = dict(jsonable_encoder(data.dict())),
                fhir_id = UUID(data.id),
                latest = True,
            )

            record = repository.find(identifier=data.id)    # Latest is implied by find
            if len(record) > 0:
                affiliation_entity.version = record[0].version + 1
            else:
                affiliation_entity.version = 1

            repository.create(affiliation_entity)
            return affiliation_entity

    def find_affiliations(
        self, affiliations_req_params: OrganizationAffiliationQueryParams
    ) -> Dict[str, Any]:
        with self.database.get_db_session() as session:
            repository = session.get_repository(OrganizationAffiliationRepository)
            affiliations = repository.find(**affiliations_req_params.model_dump())

        fhir_entities = list(map(
            lambda affiliation: OrganizationAffiliation.parse_obj(affiliation.data),
            affiliations,
        ))

        endpoint_entities = []
        # If endpoints are requested, find them and add them to the response (this could be optimized)
        if affiliations_req_params.include is not None and "Organization.endpoint" in affiliations_req_params.include:
            endpoint_entities = self._fetch_endpoints_if_requested(fhir_entities)

        combined_entities = fhir_entities + endpoint_entities

        return create_fhir_bundle(bundled_entries=combined_entities).dict()  # type: ignore

    def _fetch_endpoints_if_requested(
        self, fhir_entities: list[OrganizationAffiliation]
    ) -> list[Endpoint]:
        endpoint_entities = []

        with self.database.get_db_session() as session:
            for affiliation in fhir_entities:
                if affiliation.endpoint is None:
                    continue

                for endpoint in affiliation.endpoint:
                    endpoint_id = endpoint.reference.split("/")[1]  # type: ignore

                    endpoint_entity = session.get_repository(EndpointsRepository).find(identifier=endpoint_id)
                    if endpoint_entity[0] is None or endpoint_entity[0].data is None:
                        raise ResourceNotFoundException(f"Endpoint not found: {endpoint_id}")

                    if len(endpoint_entity) > 0:
                        endpoint_entities.append(Endpoint(**endpoint_entity[0].data))
        return endpoint_entities
