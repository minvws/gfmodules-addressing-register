import logging
from datetime import datetime
from typing import Sequence
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from fhir.resources.R4B.fhirtypes import Id
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization as FhirOrganization

from app.data import UraNumber
from app.db.db import Database
from app.db.entities.organization.organization import Organization
from app.db.repositories.endpoints_repository import EndpointsRepository
from app.db.repositories.organizations_repository import OrganizationsRepository
from app.exceptions.service_exceptions import (
    InvalidResourceException,
    ResourceNotDeletedException,
    ResourceNotFoundException,
)
from app.services.entity_services.abstraction import EntityService
from app.services.reference_validator import ReferenceValidator


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
        return isinstance(identifier, Identifier) and "http://fhir.nl/fhir/NamingSystem/ura" in identifier.system

    @staticmethod
    def get_ura_number(identifier: Identifier) -> UraNumber:
        try:
            return UraNumber(identifier.value)
        except ValueError as e:
            logging.warning(f"URA number {identifier.value} malformed: {e}")
            raise InvalidResourceException(f"URA number {identifier.value} malformed: {e}")

    @staticmethod
    def check_existing_organization(
        ura_number: UraNumber,
        organization_fhir: FhirOrganization,
        is_update: bool,
        org_repo: OrganizationsRepository,
    ) -> None:
        existing_org = org_repo.get_one(fhir_id=str(organization_fhir.id)) if is_update else None
        if existing_org and str(ura_number) != existing_org.ura_number:
            raise InvalidResourceException("URA number mismatch in new resource")

        if not is_update and org_repo.get_one(ura_number=str(ura_number)) is not None:
            raise InvalidResourceException("URA number already present in other organization")

    @staticmethod
    def validate_ura_number_in_fhir_resource(
        organization_fhir: FhirOrganization,
        is_update: bool,
        org_repo: OrganizationsRepository,
    ) -> UraNumber:
        for identifier in organization_fhir.identifier:
            if not isinstance(identifier, Identifier):
                raise InvalidResourceException("Reference identifier must be an instance of Identifier")
            if OrganizationService.is_valid_identifier(identifier):
                ura_number = OrganizationService.get_ura_number(identifier)
                OrganizationService.check_existing_organization(ura_number, organization_fhir, is_update, org_repo)
                return ura_number
        logging.error("URA number not found in organization resource")

        raise InvalidResourceException("URA number not found in organization resource")

    def add_one(self, organization_fhir: FhirOrganization) -> Organization:
        with self.database.get_db_session() as session:
            org_repo = session.get_repository(OrganizationsRepository)

            organization_fhir.meta = None  # type: ignore

            ura_number = self.validate_ura_number_in_fhir_resource(organization_fhir, False, org_repo)
            org = org_repo.get_one(ura_number=str(ura_number))
            if org is not None:
                raise InvalidResourceException("Ura number already exists")

            organization_id = uuid4()
            organization_fhir.id = Id(str(organization_id))

            self._check_references(organization_fhir)

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
                raise ResourceNotFoundException(f"Organization not found for {str(resource_id)}")

            return organization

    def get_one_version(self, resource_id: UUID, version_id: int) -> Organization:
        with self.database.get_db_session() as session:
            repository = session.get_repository(OrganizationsRepository)
            version = repository.get(fhir_id=resource_id, version=version_id)
            if version is None:
                logging.warning(f"Version not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Version not found for {str(resource_id)}")

            return version

    def update_one(
        self,
        resource_id: UUID,
        organization_fhir: FhirOrganization,
    ) -> Organization:
        with self.database.get_db_session() as session:
            org_repo = session.get_repository(OrganizationsRepository)

            organization_fhir.meta = None  # type: ignore

            self.validate_ura_number_in_fhir_resource(organization_fhir, True, org_repo)

            update_organization = org_repo.get_one(fhir_id=resource_id)
            if update_organization is None or update_organization.data is None:
                logging.warning(f"Organization not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Organization not found for {str(resource_id)}")
            meta_copy = update_organization.data.pop("meta")
            if jsonable_encoder(update_organization.data) == jsonable_encoder(organization_fhir.dict()):
                update_organization.data["meta"] = meta_copy
                return update_organization  # The old and the new are the same, no need to create a new version for this

            self._check_references(organization_fhir)

            updated_org = org_repo.update(update_organization, organization_fhir.dict())
            return updated_org

    def delete_one(self, resource_id: UUID) -> None:
        with self.database.get_db_session() as session:
            org_repo = session.get_repository(OrganizationsRepository)
            organization = org_repo.get_one(fhir_id=str(resource_id))

            if organization is None or organization.data is None:
                logging.warning(f"Organization not found for {str(resource_id)}")
                raise ResourceNotFoundException(f"Organization not found for {str(resource_id)}")

            self._check_references(FhirOrganization(**organization.data), delete=True)

            org_repo.delete(organization)

    def _check_references(self, organization: FhirOrganization, delete: bool = False) -> None:
        with self.database.get_db_session() as session:
            endpoint_repo = session.get_repository(EndpointsRepository)
            org_repo = session.get_repository(OrganizationsRepository)
            if delete:
                endpoints_with_org = endpoint_repo.find(latest=True, managingOrganization=str(organization.id))
                if len(endpoints_with_org) > 0:
                    logging.warning(
                        "Cannot delete, Endpoint %s has active reference to this resource",
                        endpoints_with_org[0].fhir_id,
                    )
                    raise ResourceNotDeletedException(
                        f"Cannot delete, Endpoint {endpoints_with_org[0].fhir_id} has active reference to this resource"
                    )
                orgs_part_of = org_repo.find(latest=True, part_of=str(organization.id))
                if len(orgs_part_of) > 0:
                    logging.warning(
                        "Cannot delete, Organization %s has active reference to this resource",
                        orgs_part_of[0].fhir_id,
                    )
                    raise ResourceNotDeletedException(
                        f"Cannot delete, Organization {orgs_part_of[0].fhir_id} has active reference to this resource"
                    )
                return

            reference_validator = ReferenceValidator()
            if organization.endpoint is not None:
                reference_validator.validate_list(
                    session,
                    [endpoint for endpoint in organization.endpoint],
                    match_on="Endpoint",
                )
            if organization.partOf is not None:
                reference_validator.validate_reference(session, organization.partOf, match_on="Organization")
