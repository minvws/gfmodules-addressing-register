import logging
from datetime import datetime
from typing import Sequence
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from fhir.resources.R4B.endpoint import Endpoint as FhirEndpoint
from fhir.resources.R4B.fhirtypes import Id
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization as FhirOrganization
from fhir.resources.R4B.reference import Reference

from app.data import UraNumber
from app.db.db import Database
from app.db.entities.organization.organization import Organization
from app.db.repositories.endpoints_repository import EndpointsRepository
from app.db.repositories.organizations_repository import OrganizationsRepository
from app.exceptions.service_exceptions import (
    ResourceNotFoundException,
    InvalidResourceException,
)
from app.services.entity_services.abstraction import EntityService


class OrganizationService(EntityService):
    def __init__(self, database: Database):
        super().__init__(database)

    def find(
        self,
        id: UUID | None = None,
        updated_at: str | None = None,
        active: bool | None = None,
        address: str | None = None,
        address_city: str | None = None,
        address_country: str | None = None,
        address_postal_code: str | None = None,
        address_state: str | None = None,
        address_use: str | None = None,
        endpoint: str | None = None,
        ura_number: str | None = None,
        name: str | None = None,
        parent_organization_id: str | None = None,
        phonetic: str | None = None,
        type: str | None = None,
        latest_version: bool | None = None,
        sort_history: bool = False,
        since: datetime | None = None,
    ) -> Sequence[Organization]:
        params = {
            "id": id,
            "updated_at": updated_at,
            "active": active,
            "address": address,
            "address_city": address_city,
            "address_country": address_country,
            "address_postal_code": address_postal_code,
            "address_state": address_state,
            "address_use": address_use,
            "endpoint": endpoint,
            "identifier": ura_number,
            "name": name,
            "part_of": parent_organization_id,
            "phonetic": phonetic,
            "type": type,
            "latest": latest_version,
            "sort_history": sort_history,
            "since": since,
        }

        filtered_params = {k: v for k, v in params.items() if v is not None}
        with self.database.get_db_session() as session:
            organization_repository = session.get_repository(OrganizationsRepository)
            return organization_repository.find(**filtered_params)

    @staticmethod
    def is_valid_identifier(identifier: Identifier) -> bool:
        return (
            isinstance(identifier, Identifier)
            and "http://fhir.nl/fhir/NamingSystem/ura" in identifier.system
        )

    @staticmethod
    def get_ura_number(identifier: Identifier) -> UraNumber:
        try:
            return UraNumber(identifier.value)
        except ValueError as e:
            logging.warning(f"URA number {identifier.value} malformed: {e}")
            raise InvalidResourceException(
                f"URA number {identifier.value} malformed: {e}"
            )

    @staticmethod
    def check_existing_organization(
        ura_number: UraNumber,
        organization_fhir: FhirOrganization,
        is_update: bool,
        org_repo: OrganizationsRepository,
    ) -> None:
        existing_org = (
            org_repo.get_one(fhir_id=str(organization_fhir.id)) if is_update else None
        )
        if existing_org and str(ura_number) != existing_org.ura_number:
            raise InvalidResourceException("URA number mismatch in new resource")

        if not is_update and org_repo.get_one(ura_number=str(ura_number)) is not None:
            raise InvalidResourceException(
                "URA number already present in other organization"
            )

    @staticmethod
    def validate_ura_number_in_fhir_resource(
        organization_fhir: FhirOrganization,
        is_update: bool,
        org_repo: OrganizationsRepository,
    ) -> UraNumber:
        for identifier in organization_fhir.identifier:
            if not isinstance(identifier, Identifier):
                raise InvalidResourceException(
                    "Reference identifier must be an instance of Identifier"
                )
            if OrganizationService.is_valid_identifier(identifier):
                ura_number = OrganizationService.get_ura_number(identifier)
                OrganizationService.check_existing_organization(
                    ura_number, organization_fhir, is_update, org_repo
                )
                return ura_number
        logging.error("URA number not found in organization resource")

        raise InvalidResourceException("URA number not found in organization resource")

    @classmethod
    def get_endpoint_ids(
        cls,
        organization_fhir: FhirOrganization,
    ) -> list[UUID]:
        endpoint_ids: list[UUID] = []
        if organization_fhir.endpoint is not None:
            for ref in organization_fhir.endpoint:
                if not isinstance(ref, Reference):
                    raise TypeError("organization reference is not a correct Type")

                reference = ref.reference

                if not reference.startswith("Endpoint/"):
                    logging.warning(f"Invalid reference for endpoint {reference}")
                    raise InvalidResourceException(
                        f"Invalid reference for endpoint {reference}"
                    )

                endpoint_id = reference.replace("Endpoint/", "")
                endpoint_ids.append(UUID(endpoint_id))
        return endpoint_ids

    @classmethod
    def add_endpoint_references(
        cls, endpoints: list[UUID], org_id: UUID, endpoint_repo: EndpointsRepository
    ) -> None:
        for endpoint_id in endpoints:
            endpoint = endpoint_repo.get_one(fhir_id=endpoint_id)
            if endpoint is None or endpoint.data is None:
                logging.warning(f"Endpoint not found for {str(endpoint_id)}")
                raise ResourceNotFoundException(
                    f"Endpoint not found for {str(endpoint_id)}"
                )
            if endpoint.data.get(
                "managingOrganization"
            ) is not None and endpoint.data.get("managingOrganization") != {
                "reference": f"Organization/{str(org_id)}"
            }:
                raise InvalidResourceException(
                    f"Endpoint {str(endpoint.fhir_id)} already has a different managing organization"
                )

            fhir_endpoint = FhirEndpoint(**endpoint.data)
            fhir_endpoint.meta = None  # type: ignore
            ref = Reference.construct(reference=f"Organization/{org_id}")
            fhir_endpoint.managingOrganization = ref  # type: ignore

            endpoint_repo.update(endpoint, fhir_endpoint.dict())

    def add_one(self, organization_fhir: FhirOrganization) -> Organization:
        with self.database.get_db_session() as session:
            org_repo = session.get_repository(OrganizationsRepository)
            endpoint_repo = session.get_repository(EndpointsRepository)

            organization_fhir.meta = None  # type: ignore

            ura_number = self.validate_ura_number_in_fhir_resource(
                organization_fhir, False, org_repo
            )
            org = org_repo.get_one(ura_number=str(ura_number))
            if org is not None:
                raise InvalidResourceException("Ura number already exists")

            organization_id = uuid4()
            organization_fhir.id = Id(str(organization_id))

            endpoint_ids = self.get_endpoint_ids(
                organization_fhir,
            )

            self.add_endpoint_references(endpoint_ids, organization_id, endpoint_repo)

            organization_instance = Organization(
                version=1,
                fhir_id=organization_id,
                ura_number=str(ura_number),
                data=jsonable_encoder(organization_fhir.dict()),
            )
            created_org = org_repo.create(organization_instance)

            return created_org

    def get_one(self, resource_id: UUID) -> Organization:
        with self.database.get_db_session() as session:
            repository = session.get_repository(OrganizationsRepository)
            organization = repository.get_one(fhir_id=str(resource_id))
            if organization is None or organization.data is None:
                logging.warning(f"Organization not found for {str(resource_id)}")
                raise ResourceNotFoundException(
                    f"Organization not found for {str(resource_id)}"
                )

            return organization

    def get_one_version(self, resource_id: UUID, version_id: int) -> Organization:
        with self.database.get_db_session() as session:
            repository = session.get_repository(OrganizationsRepository)
            version = repository.get(fhir_id=resource_id, version=version_id)
            if version is None:
                logging.warning(f"Version not found for {str(resource_id)}")
                raise ResourceNotFoundException(
                    f"Version not found for {str(resource_id)}"
                )

            return version

    def update_one(
        self,
        resource_id: UUID,
        organization_fhir: FhirOrganization,
    ) -> Organization:
        with self.database.get_db_session() as session:
            org_repo = session.get_repository(OrganizationsRepository)
            endpoint_repo = session.get_repository(EndpointsRepository)

            organization_fhir.meta = None  # type: ignore

            self.validate_ura_number_in_fhir_resource(organization_fhir, True, org_repo)

            update_organization = org_repo.get_one(fhir_id=resource_id)
            if update_organization is None or update_organization.data is None:
                logging.warning(f"Organization not found for {str(resource_id)}")
                raise ResourceNotFoundException(
                    f"Organization not found for {str(resource_id)}"
                )
            update_organization.data.pop("meta")
            if jsonable_encoder(update_organization.data) == jsonable_encoder(
                organization_fhir.dict()
            ):
                return update_organization  # The old and the new are the same, no need to create a new version for this

            endpoint_ids = self.get_endpoint_ids(
                organization_fhir,
            )

            old_endpoints = self.get_endpoint_ids(
                FhirOrganization(**update_organization.data),
            )

            # Remove endpoints that were in the previous one, but are not in
            # the updated one, which means that they need to be deleted
            endpoints_to_delete = [
                endpoint for endpoint in old_endpoints if endpoint not in endpoint_ids
            ]
            endpoints_to_add = [
                endpoint for endpoint in endpoint_ids if endpoint not in old_endpoints
            ]

            if endpoints_to_delete:
                self.delete_endpoints(endpoints_to_delete, endpoint_repo)
            if endpoints_to_add:
                self.add_endpoint_references(endpoint_ids, resource_id, endpoint_repo)

            updated_org = org_repo.update(update_organization, organization_fhir.dict())
            return updated_org

    def delete_one(self, resource_id: UUID) -> None:
        with self.database.get_db_session() as session:
            org_repo = session.get_repository(OrganizationsRepository)
            endpoint_repo = session.get_repository(EndpointsRepository)
            organization = org_repo.get_one(fhir_id=str(resource_id))

            if organization is None or organization.data is None:
                logging.warning(f"Organization not found for {str(resource_id)}")
                raise ResourceNotFoundException(
                    f"Organization not found for {str(resource_id)}"
                )

            endpoint_ids = self.get_endpoint_ids(
                organization_fhir=FhirOrganization(**organization.data),
            )

            self.delete_endpoints(endpoint_ids, endpoint_repo)

            org_repo.delete(organization)

    @staticmethod
    def delete_endpoints(
        endpoint_ids: list[UUID], endpoint_repo: EndpointsRepository
    ) -> None:
        for endpoint_id in endpoint_ids:
            endpoint = endpoint_repo.get_one(fhir_id=endpoint_id)
            if endpoint is None or endpoint.data is None:
                logging.warning(f"Endpoint not found for {str(endpoint_id)}")
                raise ResourceNotFoundException(
                    f"Endpoint not found for {str(endpoint_id)}"
                )
            endpoint_repo.delete(endpoint)
