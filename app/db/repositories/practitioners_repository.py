import logging
from datetime import UTC, datetime
from typing import Any, Dict, Sequence
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import TIMESTAMP, Boolean, String, cast, select, text
from sqlalchemy.exc import DatabaseError

from app.db.decorator import repository
from app.db.entities.practitioner.practitioner import (
    Practitioner,
)
from app.db.repositories.repository_base import RepositoryBase
from app.services.utils import update_resource_meta

logger = logging.getLogger(__name__)


@repository(Practitioner)
class PractitionerRepository(RepositoryBase):
    def get_one(self, **kwargs: bool | str | UUID | dict[str, str]) -> Practitioner | None:
        stmt = (
            select(Practitioner)
            .where(
                Practitioner.latest.__eq__(True),
                Practitioner.deleted.__eq__(False),
            )
            .filter_by(**kwargs)
        )
        return self.db_session.session.execute(stmt).scalars().first()

    def get(self, **kwargs: bool | str | UUID | dict[str, str] | int) -> Practitioner | None:
        """
        does not apply filters on latest and deleted columns.
        """
        stmt = select(Practitioner).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().first()

    def get_many(self, **kwargs: bool | str | UUID | dict[str, str]) -> Sequence[Practitioner]:
        stmt = select(Practitioner).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().all()

    def find(
        self,
        **conditions: bool | str | UUID | dict[str, Any] | datetime | None,
    ) -> Sequence[Practitioner]:
        stmt = select(Practitioner)
        filter_conditions: list[Any] = []

        conditions = {k: v for k, v in conditions.items() if v is not None}

        if "latest" in conditions and conditions["latest"] is True:
            filter_conditions.append(Practitioner.latest)
            filter_conditions.append(Practitioner.deleted.is_(False))

        if "id" in conditions and conditions["id"] is not None:
            # Filter on our internal UUID id
            filter_conditions.append(Practitioner.fhir_id == conditions["id"])

        if "active" in conditions and conditions["active"] is not None:
            filter_conditions.append(Practitioner.data["active"].astext.cast(Boolean) == conditions["active"])

        if "name" in conditions and conditions["name"] is not None:
            term = conditions["name"]
            filter_conditions.append(cast(Practitioner.data["name"].astext, String).ilike(f"%{term}%"))

        if "given" in conditions and conditions["given"] is not None:
            term = conditions["given"]
            filter_conditions.append(
                text(
                    """
                    EXISTS (
                        SELECT 1
                        FROM jsonb_array_elements(data->'name') AS name_element,
                             jsonb_array_elements_text(name_element->'given') AS given_name
                        WHERE given_name ILIKE :search_term_given
                    )
                """
                ).bindparams(search_term_given=f"%{term}%")
            )

        if "family" in conditions and conditions["family"] is not None:
            term = conditions["family"]
            filter_conditions.append(
                text(
                    """
                    EXISTS (
                        SELECT 1
                        FROM jsonb_array_elements(data->'name') AS name_element
                        WHERE name_element->>'family' ILIKE :search_term_family
                    )
                """
                ).bindparams(search_term_family=f"%{term}%")
            )

        if "sort_history" in conditions and conditions["sort_history"] is True:
            # sorted with oldest versions last
            stmt = stmt.order_by(
                cast(
                    Practitioner.data["meta"]["lastUpdated"].astext,
                    TIMESTAMP(timezone=True),
                ).desc(),
                Practitioner.version.desc(),
            )

        if "since" in conditions:
            filter_conditions.append(
                cast(
                    Practitioner.data["meta"]["lastUpdated"].astext,
                    TIMESTAMP(timezone=True),
                )
                >= conditions["since"]
            )

        stmt = stmt.where(*filter_conditions)
        return self.db_session.session.execute(stmt).scalars().all()

    def create(self, practitioner: Practitioner) -> Practitioner:
        try:
            entry = update_resource_meta(practitioner, method="create")
            self.db_session.add(entry)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add practitioner {practitioner.id}: {e}")
            raise e
        return practitioner

    def delete(self, practitioner: Practitioner) -> None:
        try:
            self._update_entry_latest(practitioner)
            updated_practitioner = Practitioner(
                fhir_id=practitioner.fhir_id,
                data=None,
                version=practitioner.version,
            )
            entry = update_resource_meta(updated_practitioner, method="delete")
            self.db_session.add(entry)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to delete practitioner {practitioner.id}: {e}")
            raise e

    def update(
        self,
        practitioner: Practitioner,
        fhir_data: Dict[str, Any],
    ) -> Practitioner:
        try:
            self._update_entry_latest(practitioner)
            entity = Practitioner(
                fhir_id=practitioner.fhir_id,
                data=jsonable_encoder(fhir_data),
                version=practitioner.version,
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
            logging.error(f"Failed to update practitioner {practitioner.id}: {e}")
            raise e

    def _update_entry_latest(self, practitioner: Practitioner) -> None:
        (
            self.db_session.query(Practitioner)
            .filter(
                Practitioner.fhir_id == practitioner.fhir_id,
                Practitioner.latest,
            )
            .update({Practitioner.latest: False})
        )
