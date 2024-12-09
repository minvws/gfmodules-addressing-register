import logging
from typing import Any, List, Sequence
from uuid import UUID

from sqlalchemy import Boolean, select
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.expression import ColumnElement

from app.db.decorator import repository
from app.db.entities.organization_affiliation.organization_affiliation import (
    OrganizationAffiliationEntry,
)
from app.db.repositories.repository_base import RepositoryBase

logger = logging.getLogger(__name__)


def convert_specialty_to_code(specialty: str) -> List[str] | None:
    conversion_table = {
        "Radiology": ["http://snomed.info/sct", "394914008"],
        "General medical practice": ["http://snomed.info/sct", "408443003"],
    }

    if specialty in conversion_table:
        return conversion_table[specialty]

    return None


@repository(OrganizationAffiliationEntry)
class OrganizationAffiliationRepository(RepositoryBase):
    def create(
        self, data: OrganizationAffiliationEntry
    ) -> OrganizationAffiliationEntry:
        try:
            # Update the latest flag for the previous version
            (
                self.db_session.query(OrganizationAffiliationEntry)
                .filter(
                    OrganizationAffiliationEntry.fhir_id == data.fhir_id,
                    OrganizationAffiliationEntry.latest,
                )
                .update({OrganizationAffiliationEntry.latest: False})
            )

            # And add new version
            self.db_session.add(data)
            self.db_session.commit()
            return data
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add OrganizationAffiliation {data.id}: {e}")
            raise e

    def find(
        self, **conditions: bool | str | UUID | dict[str, Any]
    ) -> Sequence[OrganizationAffiliationEntry]:
        stmt = select(OrganizationAffiliationEntry)

        filter_conditions: List[ColumnElement[bool] | InstrumentedAttribute[bool]] = [
            # Always use latest version
            OrganizationAffiliationEntry.latest
        ]

        if "id" in conditions and conditions["id"] is not None:
            # Filter on our internal UUID id
            filter_conditions.append(
                OrganizationAffiliationEntry.id == conditions["id"]
            )
        if "active" in conditions and conditions["active"] is not None:
            filter_conditions.append(
                OrganizationAffiliationEntry.data["active"].astext.cast(Boolean)
                == conditions["active"]
            )
        if "date" in conditions and conditions["date"] is not None:
            filter_conditions.append(
                OrganizationAffiliationEntry.created_at >= conditions["date"]
            )
        if "identifier" in conditions and conditions["identifier"] is not None:
            filter_conditions.append(
                OrganizationAffiliationEntry.fhir_id == conditions["identifier"]
            )
        if (
            "participating_organization" in conditions
            and conditions["participating_organization"] is not None
        ):
            filter_conditions.append(
                OrganizationAffiliationEntry.data["participatingOrganization"][
                    "reference"
                ].astext
                == "Organization/" + str(conditions["participating_organization"])
            )
        if (
            "primary_organization" in conditions
            and conditions["primary_organization"] is not None
        ):
            filter_conditions.append(
                OrganizationAffiliationEntry.data["organization"]["reference"].astext
                == "Organization/" + str(conditions["primary_organization"])
            )
        if "role" in conditions and conditions["role"] is not None:
            filter_conditions.append(
                OrganizationAffiliationEntry.data["code"].contains(
                    [{"coding": [{"code": conditions["role"]}]}]
                )
            )
        if "specialty" in conditions and conditions["specialty"] is not None:
            coding = convert_specialty_to_code(str(conditions["specialty"]))
            if coding:
                filter_conditions.append(
                    OrganizationAffiliationEntry.data["specialty"].contains(
                        [{"coding": [{"system": coding[0]}, {"code": coding[1]}]}]
                    )
                )

        stmt = stmt.where(*filter_conditions).limit(100)
        return self.db_session.session.execute(stmt).scalars().all()
