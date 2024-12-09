import logging
from datetime import UTC, datetime
from typing import Any, Dict, List, Sequence
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import TIMESTAMP, Boolean, cast, select
from sqlalchemy.exc import DatabaseError

from app.db.decorator import repository
from app.db.entities.organization_affiliation.organization_affiliation import (
    OrganizationAffiliation,
)
from app.db.repositories.repository_base import RepositoryBase
from app.services.utils import update_resource_meta

logger = logging.getLogger(__name__)


def convert_specialty_to_code(specialty: str) -> List[str] | None:
    conversion_table = {
        "Radiology": ["http://snomed.info/sct", "394914008"],
        "General medical practice": ["http://snomed.info/sct", "408443003"],
    }

    if specialty in conversion_table:
        return conversion_table[specialty]

    return None


@repository(OrganizationAffiliation)
class OrganizationAffiliationRepository(RepositoryBase):
    def get_one(self, **kwargs: bool | str | UUID | dict[str, str]) -> OrganizationAffiliation | None:
        stmt = (
            select(OrganizationAffiliation)
            .where(
                OrganizationAffiliation.latest.__eq__(True),
                OrganizationAffiliation.deleted.__eq__(False),
            )
            .filter_by(**kwargs)
        )
        return self.db_session.session.execute(stmt).scalars().first()

    def get(self, **kwargs: bool | str | UUID | dict[str, str] | int) -> OrganizationAffiliation | None:
        """
        does not apply filters on latest and deleted columns.
        """
        stmt = select(OrganizationAffiliation).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().first()

    def get_many(self, **kwargs: bool | str | UUID | dict[str, str]) -> Sequence[OrganizationAffiliation]:
        stmt = select(OrganizationAffiliation).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().all()

    def find(
        self,
        **conditions: bool | str | UUID | dict[str, Any] | datetime | None,
    ) -> Sequence[OrganizationAffiliation]:
        stmt = select(OrganizationAffiliation)
        filter_conditions: list[Any] = []

        conditions = {k: v for k, v in conditions.items() if v is not None}

        if "latest" in conditions and conditions["latest"] is True:
            filter_conditions.append(OrganizationAffiliation.latest)
            filter_conditions.append(OrganizationAffiliation.deleted.is_(False))

        if "id" in conditions and conditions["id"] is not None:
            # Filter on our internal UUID id
            filter_conditions.append(OrganizationAffiliation.fhir_id == conditions["id"])

        if "active" in conditions and conditions["active"] is not None:
            filter_conditions.append(
                OrganizationAffiliation.data["active"].astext.cast(Boolean) == conditions["active"]
            )

        if "date" in conditions and conditions["date"] is not None:
            filter_conditions.append(OrganizationAffiliation.created_at >= conditions["date"])

        if "participating_organization" in conditions and conditions["participating_organization"] is not None:
            filter_conditions.append(
                OrganizationAffiliation.data["participatingOrganization"]["reference"].astext
                == "Organization/" + str(conditions["participating_organization"])
            )

        if "primary_organization" in conditions and conditions["primary_organization"] is not None:
            filter_conditions.append(
                OrganizationAffiliation.data["organization"]["reference"].astext
                == "Organization/" + str(conditions["primary_organization"])
            )

        if "role" in conditions and conditions["role"] is not None:
            filter_conditions.append(
                OrganizationAffiliation.data["code"].contains([{"coding": [{"code": conditions["role"]}]}])
            )

        if "specialty" in conditions and conditions["specialty"] is not None:
            coding = convert_specialty_to_code(str(conditions["specialty"]))
            if coding:
                filter_conditions.append(
                    OrganizationAffiliation.data["specialty"].contains(
                        [{"coding": [{"system": coding[0]}, {"code": coding[1]}]}]
                    )
                )

        if "sort_history" in conditions and conditions["sort_history"] is True:
            # sorted with oldest versions last
            stmt = stmt.order_by(
                cast(
                    OrganizationAffiliation.data["meta"]["lastUpdated"].astext,
                    TIMESTAMP(timezone=True),
                ).desc(),
                OrganizationAffiliation.version.desc(),
            )

        if "since" in conditions:
            filter_conditions.append(
                cast(
                    OrganizationAffiliation.data["meta"]["lastUpdated"].astext,
                    TIMESTAMP(timezone=True),
                )
                >= conditions["since"]
            )

        stmt = stmt.where(*filter_conditions)
        return self.db_session.session.execute(stmt).scalars().all()

    def create(self, organization_affiliation: OrganizationAffiliation) -> OrganizationAffiliation:
        try:
            entry = update_resource_meta(organization_affiliation, method="create")
            self.db_session.add(entry)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add organization_affiliation {organization_affiliation.id}: {e}")
            raise e
        return organization_affiliation

    def delete(self, organization_affiliation: OrganizationAffiliation) -> None:
        try:
            self._update_entry_latest(organization_affiliation)
            updated_organization_affiliation = OrganizationAffiliation(
                fhir_id=organization_affiliation.fhir_id,
                data=None,
                version=organization_affiliation.version,
            )
            entry = update_resource_meta(updated_organization_affiliation, method="delete")
            self.db_session.add(entry)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to delete organization_affiliation {organization_affiliation.id}: {e}")
            raise e

    def update(
        self,
        organization_affiliation: OrganizationAffiliation,
        fhir_data: Dict[str, Any],
    ) -> OrganizationAffiliation:
        try:
            self._update_entry_latest(organization_affiliation)
            entity = OrganizationAffiliation(
                fhir_id=organization_affiliation.fhir_id,
                data=jsonable_encoder(fhir_data),
                version=organization_affiliation.version,
            )
            entry = update_resource_meta(entity, method="update")

            # Explicitly set the created_at / modified_at as transactions will use the same timestamp for all
            # records within the same transaction
            entry.created_at = datetime.now(UTC)
            entry.modified_at = datetime.now(UTC)

            self.db_session.add(entry)
            self.db_session.commit()
            return entry
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to update organization_affiliation {organization_affiliation.id}: {e}")
            raise e

    def _update_entry_latest(self, organization_affiliation: OrganizationAffiliation) -> None:
        (
            self.db_session.query(OrganizationAffiliation)
            .filter(
                OrganizationAffiliation.fhir_id == organization_affiliation.fhir_id,
                OrganizationAffiliation.latest,
            )
            .update({OrganizationAffiliation.latest: False})
        )
