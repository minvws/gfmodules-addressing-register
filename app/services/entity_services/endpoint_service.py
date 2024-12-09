import logging
from datetime import datetime
from typing import Sequence
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from fhir.resources.R4B.endpoint import Endpoint as FhirEndpoint
from fhir.resources.R4B.fhirtypes import Id

from app.db.db import Database
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.repositories.endpoints_repository import EndpointsRepository
from app.db.repositories.organizations_repository import OrganizationsRepository
from app.exceptions.service_exceptions import (
    ResourceNotDeletedException,
    ResourceNotFoundException,
)
from app.services.reference_validator import ReferenceValidator


class EndpointService:
    def __init__(
        self,
        database: Database,
    ):
        self.database = database

    def find(
        self,
        id: UUID | None = None,
        updated_at: str | None = None,
        connection_type: str | None = None,
        identifier: str | None = None,
        name: str | None = None,
        organization: str | None = None,
        payload_type: str | None = None,
        status: str | None = None,
        latest_version: bool | None = None,
        sort_history: bool | None = None,
        since: datetime | None = None,
    ) -> Sequence[Endpoint]:
        params = {
            "id": id,
            "updated_at": updated_at,
            "connectionType": connection_type,
            "identifier": identifier,
            "name": name,
            "managingOrganization": organization,
            "payloadType": payload_type,
            "status": status,
            "latest": latest_version,
            "sort_history": sort_history,
            "since": since,
        }
        filtered_params = {k: v for k, v in params.items() if v is not None}
        with self.database.get_db_session() as session:
            endpoints_repository = session.get_repository(EndpointsRepository)
            return endpoints_repository.find(**filtered_params)

    def get_one(self, endpoint_id: UUID) -> Endpoint:
        with self.database.get_db_session() as session:
            endpoint_repo = session.get_repository(EndpointsRepository)
            endpoint = endpoint_repo.get_one(fhir_id=endpoint_id)
            if endpoint is None:
                logging.warning("Endpoint not found for %s", endpoint_id)
                raise ResourceNotFoundException(f"Endpoint not found for {endpoint_id}")
            return endpoint

    def add_one(
        self,
        endpoint_fhir: FhirEndpoint,
    ) -> Endpoint:
        with self.database.get_db_session() as session:
            endpoint_repo = session.get_repository(EndpointsRepository)

            endpoint_fhir.meta = None  # type: ignore

            resource_id = uuid4()
            endpoint_fhir.id = Id(str(resource_id))

            self._check_references(endpoint_fhir)

            endpoint = Endpoint(
                version=1,
                fhir_id=resource_id,
                data=jsonable_encoder(endpoint_fhir.dict()),
                latest=True,
            )
            new_endpoint = endpoint_repo.create(endpoint)

            return new_endpoint

    def delete_one(self, endpoint_id: UUID) -> None:
        with self.database.get_db_session() as session:
            endpoint_repo = session.get_repository(EndpointsRepository)

            endpoint = endpoint_repo.get_one(fhir_id=endpoint_id)
            if endpoint is None or endpoint.data is None:
                logging.warning("Endpoint not found for %s", endpoint_id)
                raise ResourceNotFoundException(f"Endpoint not found for {endpoint_id}")

            self._check_references(FhirEndpoint(**endpoint.data), delete=True)

            endpoint_repo.delete(endpoint)

    def update_one(
        self,
        endpoint_id: UUID,
        endpoint_fhir: FhirEndpoint,
    ) -> Endpoint:
        with self.database.get_db_session() as session:
            endpoint_repo = session.get_repository(EndpointsRepository)

            endpoint_fhir.meta = None  # type: ignore

            update_endpoint = endpoint_repo.get_one(fhir_id=endpoint_id)
            if update_endpoint is None or update_endpoint.data is None:
                logging.warning("Endpoint not found for %s", endpoint_id)
                raise ResourceNotFoundException(f"Endpoint not found for {endpoint_id}")

            update_endpoint.data.pop("meta")
            if jsonable_encoder(update_endpoint.data) == jsonable_encoder(endpoint_fhir.dict()):
                # They are the same, no need to update
                return update_endpoint

            self._check_references(endpoint_fhir)

            updated_endpoint = endpoint_repo.update(update_endpoint, endpoint_fhir.dict())

            return updated_endpoint

    def get_one_version(self, resource_id: UUID, version_id: int) -> Endpoint:
        with self.database.get_db_session() as session:
            repository = session.get_repository(EndpointsRepository)
            version = repository.get(fhir_id=resource_id, version=version_id)
            if version is None:
                logging.warning(f"Version not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Version not found for {str(resource_id)}")

            return version

    def _check_references(self, data: FhirEndpoint, delete: bool = False) -> None:
        with self.database.get_db_session() as session:
            org_repo = session.get_repository(OrganizationsRepository)
            if delete:
                orgs_with_ref_to_endpoint = org_repo.find(latest=True, endpoint=str(data.id))
                if len(orgs_with_ref_to_endpoint) > 0:
                    logging.warning(
                        "Cannot delete, Organization %s has active reference to this resource",
                        orgs_with_ref_to_endpoint[0].fhir_id,
                    )
                    raise ResourceNotDeletedException(
                        f"Cannot delete, Organization {orgs_with_ref_to_endpoint[0].fhir_id} has active reference to this resource"
                    )
                return

            if data.managingOrganization is not None:
                reference_validator = ReferenceValidator()
                reference_validator.validate_reference(session, data.managingOrganization, match_on="Organization")
