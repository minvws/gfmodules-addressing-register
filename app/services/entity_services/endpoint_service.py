import logging
from typing import Sequence
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from fhir.resources.R4B.fhirtypes import Id, ReferenceType
from fhir.resources.R4B.organization import Organization as FhirOrganization
from fhir.resources.R4B.endpoint import Endpoint as FhirEndpoint
from fhir.resources.R4B.reference import Reference

from app.db.db import Database
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.entities.organization.organization import Organization
from app.db.repositories.endpoints_repository import EndpointsRepository
from app.db.repositories.organizations_repository import OrganizationsRepository
from app.exceptions.service_exceptions import (
    ResourceNotFoundException,
    InvalidResourceException,
)


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
            org_repository = session.get_repository(OrganizationsRepository)

            endpoint_fhir.meta = None  # type: ignore

            resource_id = uuid4()
            endpoint_fhir.id = Id(str(resource_id))

            managing_org = self._get_managing_organization(
                endpoint_fhir, org_repository
            )
            if managing_org is not None:
                self._add_org_reference(managing_org, resource_id, org_repository)

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
            org_repository = session.get_repository(OrganizationsRepository)

            endpoint = endpoint_repo.get_one(fhir_id=endpoint_id)
            if endpoint is None or endpoint.data is None:
                logging.warning("Endpoint not found for %s", endpoint_id)
                raise ResourceNotFoundException(f"Endpoint not found for {endpoint_id}")

            endpoint_fhir = FhirEndpoint(**endpoint.data)
            managing_org_reference = endpoint_fhir.managingOrganization
            if managing_org_reference is not None:
                if not isinstance(managing_org_reference, Reference):
                    raise TypeError("managing_org must be Reference")

                managing_org = self._get_managing_organization(
                    endpoint_fhir, org_repository
                )
                if managing_org is not None:
                    self._remove_org_reference(
                        managing_org, endpoint_id, org_repository
                    )

            endpoint_repo.delete(endpoint)

    def update_one(
        self,
        endpoint_id: UUID,
        endpoint_fhir: FhirEndpoint,
    ) -> Endpoint:
        with self.database.get_db_session() as session:
            endpoint_repo = session.get_repository(EndpointsRepository)
            org_repository = session.get_repository(OrganizationsRepository)

            endpoint_fhir.meta = None  # type: ignore

            update_endpoint = endpoint_repo.get_one(fhir_id=endpoint_id)
            if update_endpoint is None or update_endpoint.data is None:
                logging.warning("Endpoint not found for %s", endpoint_id)
                raise ResourceNotFoundException(f"Endpoint not found for {endpoint_id}")

            update_endpoint.data.pop("meta")
            if jsonable_encoder(update_endpoint.data) == jsonable_encoder(
                endpoint_fhir.dict()
            ):
                # They are the same, no need to update
                return update_endpoint

            new_managing_org = self._get_managing_organization(
                endpoint_fhir, org_repository
            )
            old_managing_org = self._get_managing_organization(
                FhirEndpoint(**update_endpoint.data), org_repository
            )

            if old_managing_org is not None and new_managing_org is None:
                self._remove_org_reference(
                    old_managing_org, endpoint_id, org_repository
                )
            elif old_managing_org is None and new_managing_org is not None:
                self._add_org_reference(new_managing_org, endpoint_id, org_repository)
            elif old_managing_org is not None and new_managing_org is not None:
                if new_managing_org.ura_number != old_managing_org.ura_number:
                    self._remove_org_reference(
                        old_managing_org, endpoint_id, org_repository
                    )
                    self._add_org_reference(
                        new_managing_org, endpoint_id, org_repository
                    )

            updated_endpoint = endpoint_repo.update(
                update_endpoint, endpoint_fhir.dict()
            )

            return updated_endpoint

    def get_one_version(self, resource_id: UUID, version_id: int) -> Endpoint:
        with self.database.get_db_session() as session:
            repository = session.get_repository(EndpointsRepository)
            version = repository.get(fhir_id=resource_id, version=version_id)
            if version is None:
                logging.warning(f"Version not found for {str(resource_id)}")
                raise ResourceNotFoundException(
                    f"Version not found for {str(resource_id)}"
                )

            return version

    @staticmethod
    def _get_managing_organization(
        data: FhirEndpoint, repository: OrganizationsRepository
    ) -> Organization | None:
        if data.managingOrganization is None:
            return

        if not isinstance(data.managingOrganization, Reference):
            raise InvalidResourceException(
                "Managing organization reference was not found"
            )

        try:
            organization_id = UUID(
                data.managingOrganization.reference.replace("Organization/", "")
            )
        except ValueError as e:
            raise InvalidResourceException(
                f"Could not create UUID from organization id {e}"
            )
        organization = repository.get_one(fhir_id=organization_id)
        if organization is None or organization.data is None:
            raise ResourceNotFoundException(
                f"Organization {organization_id} was not found"
            )

        return organization

    @staticmethod
    def _add_org_reference(
        org: Organization,
        endpoint_fhir_id: UUID,
        repository: OrganizationsRepository,
    ) -> None:
        if org.data is None:
            raise ResourceNotFoundException(f"Organization {org.fhir_id} was not found")
        fhir_managing_org = FhirOrganization(**org.data)
        fhir_managing_org.meta = None  # type: ignore
        if fhir_managing_org.endpoint is None:
            fhir_managing_org.endpoint = []

        ref = Reference.construct(reference=f"Endpoint/{str(endpoint_fhir_id)}")
        fhir_managing_org.endpoint.append(ref)  # type: ignore

        repository.update(org, fhir_managing_org.dict())

    @staticmethod
    def _remove_org_reference(
        org: Organization,
        endpoint_fhir_id: UUID,
        repository: OrganizationsRepository,
    ) -> None:
        if org.data is None:
            raise ResourceNotFoundException(f"Organization {org.fhir_id} was not found")
        new_org_fhir = FhirOrganization(**org.data)
        new_org_fhir.meta = None  # type: ignore
        ref = ReferenceType(reference=f"Endpoint/{str(endpoint_fhir_id)}")
        index = new_org_fhir.endpoint.index(ref)
        new_org_fhir.endpoint.pop(index)

        repository.update(org, new_org_fhir.dict())
