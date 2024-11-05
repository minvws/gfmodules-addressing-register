from typing import Any, Dict
from uuid import uuid4

from fastapi.encoders import jsonable_encoder
from fhir.resources.R4B.organizationaffiliation import OrganizationAffiliation

from app.db.db import Database
from app.db.repositories.organization_affiliation_repository import OrganizationAffiliationRepository
from app.db.entities.organization_affiliation.organization_affiliation import OrganizationAffiliationEntry
from app.mappers.fhir_mapper import create_fhir_bundle, map_to_endpoint_fhir
from app.db.repositories.endpoints_repository import EndpointsRepository
from app.params.organization_affiliation_query_params import OrganizationAffiliationQueryParams


class OrganizationAffiliationService:
    def __init__(self, database: Database):
        self.database = database

    def add_one(self, data: OrganizationAffiliation) -> Dict[str, Any]:
        with self.database.get_db_session() as session:
            repository = session.get_repository(OrganizationAffiliationRepository)

            affiliation_entity = OrganizationAffiliationEntry(id=uuid4())
            affiliation_entity.data = dict(jsonable_encoder(data.dict()))
            affiliation_entity.fhir_id = data.id
            affiliation_entity.latest = True

            record = repository.find(identifier=data.id)    # Latest is implied by find
            if len(record) > 0:
                affiliation_entity.version = record[0].version + 1
            else:
                affiliation_entity.version = 1

            repository.create(affiliation_entity)
            return affiliation_entity.data

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
        with self.database.get_db_session() as session:
            for affiliation in fhir_entities:
                for endpoint in affiliation.endpoint:
                    endpoint_id = endpoint.reference.split("/")[1]  # type: ignore

                    endpoint_entity = session.get_repository(EndpointsRepository).find(identifier=endpoint_id)
                    if len(endpoint_entity) > 0:
                        endpoint_entities.append(map_to_endpoint_fhir(endpoint_entity[0]))

        combined_entities = fhir_entities + endpoint_entities

        return create_fhir_bundle(bundled_entries=combined_entities).dict()  # type: ignore
