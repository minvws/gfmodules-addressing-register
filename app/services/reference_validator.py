import logging
from typing import List

from fhir.resources.R4B.fhirtypes import ReferenceType
from fhir.resources.R4B.reference import Reference
from sqlalchemy import false, select

from app.db.entities.endpoint.endpoint import Endpoint
from app.db.entities.healthcare_service.healthcare_service import HealthcareService
from app.db.entities.location.location import Location
from app.db.entities.organization.organization import Organization
from app.db.entities.organization_affiliation.organization_affiliation import OrganizationAffiliation
from app.db.session import DbSession
from app.exceptions.service_exceptions import ResourceNotFoundException
from app.services.utils import split_reference


class ReferenceValidator:
    @staticmethod
    def validate_reference(session: DbSession, data: ReferenceType | Reference, match_on: str) -> None:
        if not isinstance(data, Reference):
            raise ValueError(f"Invalid reference {data}")

        (reference_type, reference_id) = split_reference(data.reference)
        if reference_type != match_on:
            raise ValueError(f"Invalid reference {data.reference}, expected {match_on}")

        match reference_type:
            case "HealthcareService":
                found = session.execute(
                    select(HealthcareService)
                    .where(HealthcareService.fhir_id == reference_id)
                    .where(HealthcareService.deleted == false())
                    .limit(1)
                ).first()
            case "OrganizationAffiliation":
                found = session.execute(
                    select(OrganizationAffiliation)
                    .where(OrganizationAffiliation.fhir_id == reference_id)
                    .where(OrganizationAffiliation.deleted == false())
                    .limit(1)
                ).first()
            case "Organization":
                found = session.execute(
                    select(Organization)
                    .where(Organization.fhir_id == reference_id)
                    .where(Organization.deleted == false())
                    .limit(1)
                ).first()
            case "Endpoint":
                found = session.execute(
                    select(Endpoint).where(Endpoint.fhir_id == reference_id).where(Endpoint.deleted == false()).limit(1)
                ).first()
            case "Location":
                found = session.execute(
                    select(Location).where(Location.fhir_id == reference_id).where(Location.deleted == false()).limit(1)
                ).first()
            case _:
                raise ValueError(f"Invalid reference type {reference_type}")

        if found is None:
            logging.warning("Invalid resource, reference %s is not resolvable", data.reference)
            raise ResourceNotFoundException(f"Invalid resource, reference {data.reference} is not resolvable")

    def validate_list(
        self,
        session: DbSession,
        data: List[ReferenceType] | List[Reference],
        match_on: str,
    ) -> None:
        for reference_data in data:
            self.validate_reference(session, reference_data, match_on=match_on)
