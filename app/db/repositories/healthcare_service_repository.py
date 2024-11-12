import logging
from typing import Sequence, Union, Any
from uuid import UUID

from sqlalchemy import select, Boolean
from sqlalchemy.exc import DatabaseError

from app.db.decorator import repository
from app.db.repositories.repository_base import RepositoryBase
from app.db.entities.healthcare_service.healthcare_service import HealthcareServiceEntry

logger = logging.getLogger(__name__)


@repository(HealthcareServiceEntry)
class HealthcareServiceRepository(RepositoryBase):

    def create(self, data: HealthcareServiceEntry) -> HealthcareServiceEntry:
        try:
            # Update the latest flag for the previous version
            (self.db_session.query(HealthcareServiceEntry)
                .filter(HealthcareServiceEntry.fhir_id == data.fhir_id,
                        HealthcareServiceEntry.latest
                        )
                .update({HealthcareServiceEntry.latest: False}))

            # And add new version
            self.db_session.add(data)
            self.db_session.commit()
            return data
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add HealthcareService {data.id}: {e}")
            raise e

    def find(
        self, **conditions: Union[bool, str, UUID, dict[str, Any]]
    ) -> Sequence[HealthcareServiceEntry]:
        stmt = select(HealthcareServiceEntry)

        filter_conditions = [
            # Always use latest version
            HealthcareServiceEntry.latest
        ]

        if "id" in conditions and conditions["id"] is not None:
            # Filter on our internal UUID id
            filter_conditions.append(HealthcareServiceEntry.id == conditions["id"]) # type: ignore
        if "active" in conditions and conditions["active"] is not None:
            filter_conditions.append(HealthcareServiceEntry.data["active"].astext.cast(Boolean) == conditions["active"])
        if "date" in conditions and conditions["date"] is not None:
            filter_conditions.append(HealthcareServiceEntry.created_at >= conditions["date"])   # type: ignore
        if "identifier" in conditions and conditions["identifier"] is not None:
            filter_conditions.append(HealthcareServiceEntry.fhir_id == conditions["identifier"])    # type: ignore

        stmt = (stmt.where(*filter_conditions).limit(100))
        return self.db_session.session.execute(stmt).scalars().all()
