from typing import List

from fhir.resources.R4B.reference import Reference
from fhir.resources.R4B.fhirtypes import ReferenceType

from app.db.entities.healthcare_service.healthcare_service import HealthcareServiceEntry
from app.db.entities.organization_affiliation.organization_affiliation import OrganizationAffiliationEntry
from app.db.session import DbSession


class ReferenceValidator:
    @staticmethod
    def validate_reference(session: DbSession, data: ReferenceType|Reference, reference_types: List[str]|None = None, all_allowed: bool = False) -> bool:
        if not isinstance(data, Reference):
            raise ValueError(f"Invalid reference {data}")

        parts = data.reference.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid reference {data.reference}")

        reference_type = parts[0]
        reference_id = parts[1]

        if not all_allowed:
            if reference_types is None:
                raise ValueError("Need at least one reference type")
            if reference_type not in reference_types:
                raise ValueError(f"Invalid reference {data.reference}, expected {reference_types}")

        if reference_type == "HealthcareService":
            found = session.query(HealthcareServiceEntry).filter(HealthcareServiceEntry.fhir_id == reference_id).first() is not None
        elif reference_type == "OrganizationAffiliation":
            found = session.query(OrganizationAffiliationEntry).filter(OrganizationAffiliationEntry.fhir_id == reference_id).first() is not None
        else:
            raise ValueError(f"Invalid reference type {reference_type}")

        return found

    def validate_list(self, session: DbSession, data: List[ReferenceType]|List[Reference], reference_types: List[str]|None = None, all_allowed: bool = False) -> bool:
        for reference_data in data:
            if not self.validate_reference(session, reference_data, reference_types, all_allowed):
                return False
        return True
