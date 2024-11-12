from typing import Any, Dict
from uuid import uuid4

from fastapi.encoders import jsonable_encoder
from fhir.resources.R4B.healthcareservice import HealthcareService

from app.db.db import Database
from app.mappers.fhir_mapper import create_fhir_bundle
from app.db.entities.healthcare_service.healthcare_service import HealthcareServiceEntry
from app.db.repositories.healthcare_service_repository import HealthcareServiceRepository
from app.params.healthcare_service_query_params import HealthcareServiceQueryParams


class HealthcareServiceService:
    def __init__(self, database: Database):
        self.database = database

    def add_one(self, data: HealthcareService) -> Dict[str, Any]:
        with self.database.get_db_session() as session:
            repository = session.get_repository(HealthcareServiceRepository)

            healthcare_service_entity = HealthcareServiceEntry(id=uuid4())
            healthcare_service_entity.data = dict(jsonable_encoder(data.dict()))
            healthcare_service_entity.fhir_id = data.id
            healthcare_service_entity.latest = True

            record = repository.find(identifier=data.id)    # Latest is implied by find
            if len(record) > 0:
                healthcare_service_entity.version = record[0].version + 1
            else:
                healthcare_service_entity.version = 1

            repository.create(healthcare_service_entity)
            return healthcare_service_entity.data

    def find(
        self, healthcare_service_req_params: HealthcareServiceQueryParams
    ) -> Dict[str, Any]:
        with self.database.get_db_session() as session:
            repository = session.get_repository(HealthcareServiceRepository)
            healthcare_services = repository.find(**healthcare_service_req_params.model_dump())

        fhir_entities = list(map(
            lambda healthcare_service: HealthcareService.parse_obj(healthcare_service.data),
            healthcare_services,
        ))

        return create_fhir_bundle(bundled_entries=fhir_entities).dict()  # type: ignore
