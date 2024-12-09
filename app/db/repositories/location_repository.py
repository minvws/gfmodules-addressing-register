import logging
from datetime import UTC, datetime
from typing import Any, Dict, Sequence
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import TIMESTAMP, cast, select
from sqlalchemy.exc import DatabaseError

from app.db.decorator import repository
from app.db.entities.location.location import Location
from app.db.repositories.repository_base import RepositoryBase
from app.services.utils import update_resource_meta

logger = logging.getLogger(__name__)


@repository(Location)
class LocationRepository(RepositoryBase):
    def get_one(self, **kwargs: bool | str | UUID | dict[str, str]) -> Location | None:
        stmt = select(Location).where(Location.latest.__eq__(True), Location.deleted.__eq__(False)).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().first()

    def get(self, **kwargs: bool | str | UUID | dict[str, str] | int) -> Location | None:
        """
        does not apply filters on latest and deleted columns.
        """
        stmt = select(Location).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().first()

    def get_many(self, **kwargs: bool | str | UUID | dict[str, str]) -> Sequence[Location]:
        stmt = select(Location).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().all()

    def find(
        self,
        **conditions: bool | str | UUID | dict[str, Any] | datetime | None,
    ) -> Sequence[Location]:
        stmt = select(Location)
        filter_conditions: list[Any] = []

        conditions = {k: v for k, v in conditions.items() if v is not None}

        if "latest" in conditions and conditions["latest"] is True:
            filter_conditions.append(Location.latest)
            filter_conditions.append(Location.deleted.is_(False))

        if "id" in conditions and conditions["id"] is not None:
            # Filter on our internal UUID id
            filter_conditions.append(Location.fhir_id == conditions["id"])

        if "name" in conditions and conditions["id"] is not None:
            filter_conditions.append(Location.data["name"].astext == conditions["name"])

        if "managing_organization" in conditions and conditions["managing_organization"] is not None:
            filter_conditions.append(
                Location.data["managingOrganization"]["reference"].astext
                == "Organization/" + str(conditions["managing_organization"])
            )

        if "part_of" in conditions and conditions["part_of"] is not None:
            filter_conditions.append(
                Location.data["partOf"]["reference"].astext == "Location/" + str(conditions["part_of"])
            )

        if "status" in conditions and conditions["status"] is not None:
            filter_conditions.append(Location.data["status"].astext == conditions["status"])

        if "type" in conditions and conditions["type"] is not None:
            filter_conditions.append(Location.data["type"].astext == conditions["type"])

        if "date" in conditions and conditions["date"] is not None:
            filter_conditions.append(Location.created_at >= conditions["date"])

        if "sort_history" in conditions and conditions["sort_history"] is True:
            # sorted with oldest versions last
            stmt = stmt.order_by(
                cast(Location.data["meta"]["lastUpdated"].astext, TIMESTAMP(timezone=True)).desc(),
                Location.version.desc(),
            )

        if "since" in conditions:
            filter_conditions.append(
                cast(Location.data["meta"]["lastUpdated"].astext, TIMESTAMP(timezone=True)) >= conditions["since"]
            )

        stmt = stmt.where(*filter_conditions)
        return self.db_session.session.execute(stmt).scalars().all()

    def create(self, location: Location) -> Location:
        try:
            entry = update_resource_meta(location, method="create")
            self.db_session.add(entry)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add location {location.id}: {e}")
            raise e
        return location

    def delete(self, location: Location) -> None:
        try:
            self._update_entry_latest(location)
            updated_location = Location(
                fhir_id=location.fhir_id,
                data=None,
                version=location.version,
            )
            entry = update_resource_meta(updated_location, method="delete")
            self.db_session.add(entry)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to delete location {location.id}: {e}")
            raise e

    def update(self, location: Location, fhir_data: Dict[str, Any]) -> Location:
        try:
            self._update_entry_latest(location)
            entity = Location(
                fhir_id=location.fhir_id,
                data=jsonable_encoder(fhir_data),
                version=location.version,
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
            logging.error(f"Failed to update location {location.id}: {e}")
            raise e

    def _update_entry_latest(self, location: Location) -> None:
        (
            self.db_session.query(Location)
            .filter(Location.fhir_id == location.fhir_id, Location.latest)
            .update({Location.latest: False})
        )
