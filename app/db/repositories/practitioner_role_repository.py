import logging
from datetime import UTC, datetime
from typing import Any, Dict, Sequence
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import TIMESTAMP, Boolean, cast, select
from sqlalchemy.exc import DatabaseError

from app.db.decorator import repository
from app.db.entities.practitioner_role.practitioner_role import (
    PractitionerRole,
)
from app.db.repositories.repository_base import RepositoryBase
from app.services.utils import update_resource_meta

logger = logging.getLogger(__name__)


@repository(PractitionerRole)
class PractitionerRoleRepository(RepositoryBase):
    def get_one(self, **kwargs: bool | str | UUID | dict[str, str]) -> PractitionerRole | None:
        stmt = (
            select(PractitionerRole)
            .where(
                PractitionerRole.latest.__eq__(True),
                PractitionerRole.deleted.__eq__(False),
            )
            .filter_by(**kwargs)
        )
        return self.db_session.session.execute(stmt).scalars().first()

    def get(self, **kwargs: bool | str | UUID | dict[str, str] | int) -> PractitionerRole | None:
        """
        does not apply filters on latest and deleted columns.
        """
        stmt = select(PractitionerRole).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().first()

    def get_many(self, **kwargs: bool | str | UUID | dict[str, str]) -> Sequence[PractitionerRole]:
        stmt = select(PractitionerRole).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().all()

    def find(
        self,
        **conditions: bool | str | UUID | dict[str, Any] | datetime | None,
    ) -> Sequence[PractitionerRole]:
        stmt = select(PractitionerRole)
        filter_conditions: list[Any] = []

        conditions = {k: v for k, v in conditions.items() if v is not None}

        if "latest" in conditions and conditions["latest"] is True:
            filter_conditions.append(PractitionerRole.latest)
            filter_conditions.append(PractitionerRole.deleted.is_(False))

        if "id" in conditions and conditions["id"] is not None:
            # Filter on our internal UUID id
            filter_conditions.append(PractitionerRole.fhir_id == conditions["id"])

        if "active" in conditions and conditions["active"] is not None:
            filter_conditions.append(PractitionerRole.data["active"].astext.cast(Boolean) == conditions["active"])

        if "date" in conditions and conditions["date"] is not None:
            filter_conditions.append(PractitionerRole.created_at >= conditions["date"])

        if "location" in conditions and conditions["location"] is not None:
            filter_conditions.append(
                PractitionerRole.data["location"]["reference"].astext == "Location/" + str(conditions["location"])
            )

        if "practitioner" in conditions and conditions["practitioner"] is not None:
            filter_conditions.append(
                PractitionerRole.data["practitioner"]["reference"].astext
                == "Practitioner/" + str(conditions["practitioner"])
            )

        if "organization" in conditions and conditions["organization"] is not None:
            filter_conditions.append(
                PractitionerRole.data["organization"]["reference"].astext
                == "Organization/" + str(conditions["organization"])
            )

        if "role" in conditions and conditions["role"] is not None:
            filter_conditions.append(
                PractitionerRole.data["code"].contains([{"coding": [{"code": conditions["role"]}]}])
            )

        if "service" in conditions and conditions["service"] is not None:
            filter_conditions.append(
                PractitionerRole.data["service"]["reference"].astext
                == "HealthcareService/" + str(conditions["service"])
            )

        if "specialty" in conditions and conditions["specialty"] is not None:
            filter_conditions.append(
                PractitionerRole.data["specialty"].contains([{"coding": [{"code": conditions["specialty"]}]}])
            )

        if "sort_history" in conditions and conditions["sort_history"] is True:
            # sorted with oldest versions last
            stmt = stmt.order_by(
                cast(
                    PractitionerRole.data["meta"]["lastUpdated"].astext,
                    TIMESTAMP(timezone=True),
                ).desc(),
                PractitionerRole.version.desc(),
            )

        if "since" in conditions:
            filter_conditions.append(
                cast(
                    PractitionerRole.data["meta"]["lastUpdated"].astext,
                    TIMESTAMP(timezone=True),
                )
                >= conditions["since"]
            )

        stmt = stmt.where(*filter_conditions)
        return self.db_session.session.execute(stmt).scalars().all()

    def create(self, practitioner_role: PractitionerRole) -> PractitionerRole:
        try:
            entry = update_resource_meta(practitioner_role, method="create")
            self.db_session.add(entry)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add practitioner_role {practitioner_role.id}: {e}")
            raise e
        return practitioner_role

    def delete(self, practitioner_role: PractitionerRole) -> None:
        try:
            self._update_entry_latest(practitioner_role)
            updated_practitioner_role = PractitionerRole(
                fhir_id=practitioner_role.fhir_id,
                data=None,
                version=practitioner_role.version,
            )
            entry = update_resource_meta(updated_practitioner_role, method="delete")
            self.db_session.add(entry)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to delete practitioner_role {practitioner_role.id}: {e}")
            raise e

    def update(
        self,
        practitioner_role: PractitionerRole,
        fhir_data: Dict[str, Any],
    ) -> PractitionerRole:
        try:
            self._update_entry_latest(practitioner_role)
            entity = PractitionerRole(
                fhir_id=practitioner_role.fhir_id,
                data=jsonable_encoder(fhir_data),
                version=practitioner_role.version,
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
            logging.error(f"Failed to update practitioner_role {practitioner_role.id}: {e}")
            raise e

    def _update_entry_latest(self, practitioner_role: PractitionerRole) -> None:
        (
            self.db_session.query(PractitionerRole)
            .filter(
                PractitionerRole.fhir_id == practitioner_role.fhir_id,
                PractitionerRole.latest,
            )
            .update({PractitionerRole.latest: False})
        )
