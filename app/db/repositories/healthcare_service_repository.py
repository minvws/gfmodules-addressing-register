import logging
from datetime import UTC, datetime
from typing import Any, Dict, Sequence
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import TIMESTAMP, Boolean, cast, func, select
from sqlalchemy.dialects.postgresql import JSONPATH
from sqlalchemy.exc import DatabaseError

from app.db.decorator import repository
from app.db.entities.healthcare_service.healthcare_service import HealthcareService
from app.db.repositories.repository_base import RepositoryBase
from app.services.utils import update_resource_meta

logger = logging.getLogger(__name__)


@repository(HealthcareService)
class HealthcareServiceRepository(RepositoryBase):
    def get_one(
        self, **kwargs: bool | str | UUID | dict[str, str]
    ) -> HealthcareService | None:
        stmt = (
            select(HealthcareService)
            .where(
                HealthcareService.latest.__eq__(True),
                HealthcareService.deleted.__eq__(False),
            )
            .filter_by(**kwargs)
        )
        return self.db_session.session.execute(stmt).scalars().first()

    def get(
        self, **kwargs: bool | str | UUID | dict[str, str] | int
    ) -> HealthcareService | None:
        """
        does not apply filters on latest and deleted columns.
        """
        stmt = select(HealthcareService).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().first()

    def get_many(
        self, **kwargs: bool | str | UUID | dict[str, str]
    ) -> Sequence[HealthcareService]:
        stmt = select(HealthcareService).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().all()

    def find(
        self,
        **conditions: bool | str | UUID | dict[str, Any] | None,
    ) -> Sequence[HealthcareService]:
        stmt = select(HealthcareService)
        filter_conditions: list[Any] = []

        conditions = {k: v for k, v in conditions.items() if v is not None}

        if "latest" in conditions and conditions["latest"] is True:
            filter_conditions.append(HealthcareService.latest)
            filter_conditions.append(HealthcareService.deleted.is_(False))

        if "id" in conditions:
            filter_conditions.append(HealthcareService.fhir_id == conditions["id"])

        if "active" in conditions:
            filter_conditions.append(
                HealthcareService.data["active"].astext.cast(Boolean)
                == conditions["active"]
            )

        if "organization" in conditions:
            filter_conditions.append(
                HealthcareService.data["providedBy"]["reference"].astext
                == "Organization/" + str(conditions["organization"])
            )

        if "service_type" in conditions:
            json_path = cast("$.type[*].coding[*] ? (@.code == $code)", JSONPATH)
            vars = func.jsonb_build_object("code", conditions["service_type"])
            filter_conditions.append(
                func.jsonb_path_exists(HealthcareService.data, json_path, vars)
            )

        if "location" in conditions:
            json_path = cast("$.location[*] ? (@.reference == $location_ref)", JSONPATH)
            vars = func.jsonb_build_object(
                "location_ref", "Location/" + str(conditions["location"])
            )
            filter_conditions.append(
                func.jsonb_path_exists(HealthcareService.data, json_path, vars)
            )

        if "name" in conditions:
            filter_conditions.append(
                HealthcareService.data["name"].astext.like(f'%{conditions["name"]}%')
            )

        if "sort_history" in conditions and conditions["sort_history"] is True:
            # sorted with oldest versions last
            stmt = stmt.order_by(
                cast(
                    HealthcareService.data["meta"]["lastUpdated"].astext,
                    TIMESTAMP(timezone=True),
                ).desc(),
                HealthcareService.version.desc(),
            )

        if "since" in conditions:
            filter_conditions.append(
                cast(
                    HealthcareService.data["meta"]["lastUpdated"].astext,
                    TIMESTAMP(timezone=True),
                )
                >= conditions["since"]
            )

        stmt = stmt.where(*filter_conditions)
        return self.db_session.session.execute(stmt).scalars().all()

    def create(self, healthcare_service: HealthcareService) -> HealthcareService:
        try:
            entry = update_resource_meta(healthcare_service, method="create")
            self.db_session.add(entry)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(
                f"Failed to add healthcare_service {healthcare_service.id}: {e}"
            )
            raise e
        return healthcare_service

    def delete(self, healthcare_service: HealthcareService) -> None:
        try:
            self._update_entry_latest(healthcare_service)
            updated_healthcare_service = HealthcareService(
                fhir_id=healthcare_service.fhir_id,
                data=None,
                version=healthcare_service.version,
            )
            entry = update_resource_meta(updated_healthcare_service, method="delete")
            self.db_session.add(entry)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(
                f"Failed to delete healthcare_service {healthcare_service.id}: {e}"
            )
            raise e

    def update(
        self, healthcare_service: HealthcareService, fhir_data: Dict[str, Any]
    ) -> HealthcareService:
        try:
            self._update_entry_latest(healthcare_service)
            entity = HealthcareService(
                fhir_id=healthcare_service.fhir_id,
                data=jsonable_encoder(fhir_data),
                version=healthcare_service.version,
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
            logging.error(
                f"Failed to update healthcare_service {healthcare_service.id}: {e}"
            )
            raise e

    def _update_entry_latest(self, healthcare_service: HealthcareService) -> None:
        (
            self.db_session.query(HealthcareService)
            .filter(
                HealthcareService.fhir_id == healthcare_service.fhir_id,
                HealthcareService.latest,
            )
            .update({HealthcareService.latest: False})
        )
