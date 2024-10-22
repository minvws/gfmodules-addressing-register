import logging
from datetime import datetime
from typing import Any, Sequence, Union
from uuid import UUID

from sqlalchemy import Boolean, select, and_, func, literal_column
from sqlalchemy.exc import DatabaseError

from app.db.decorator import repository
from app.db.entities.organization.history import OrganizationHistory
from app.db.repositories.repository_base import RepositoryBase

logger = logging.getLogger(__name__)


@repository(OrganizationHistory)
class OrganizationHistoryRepository(RepositoryBase):
    def create(self, history: OrganizationHistory) -> OrganizationHistory:
        try:
            self.db_session.add(history)
            self.db_session.commit()
            return history
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add organization {history.ura_number}: {e}")
            raise e

    def find(self, **conditions: Union[bool, str, UUID, dict[str, Any], datetime]) -> Sequence[OrganizationHistory]:
        filter_conditions = []
        stmt = (
            select(OrganizationHistory)
        )
        if "id" in conditions:
            filter_conditions.append(OrganizationHistory.id == conditions["id"])
        if "organization_id" in conditions:
            filter_conditions.append(OrganizationHistory.organization_id == conditions["organization_id"])
        if "identifier" in conditions:
            filter_conditions.append(OrganizationHistory.ura_number == conditions["identifier"])
        if "since" in conditions:
            filter_conditions.append(OrganizationHistory.created_at >= conditions["since"])
        if "active" in conditions:
            filter_conditions.append(OrganizationHistory.data["active"].astext.cast(Boolean) == conditions["active"])


        if "endpoint_id" in conditions:
            sub_stmt = (
                select(
                    OrganizationHistory.id
                )
                .select_from(
                    OrganizationHistory,
                    func.json_array_elements(OrganizationHistory.data['endpoint']).alias('endpoint')
                )
                .where(
                    literal_column("endpoint->>'reference'") == "Endpoint/" + conditions["endpoint_id"] # type: ignore
                )
            )
            results = self.db_session.session.execute(sub_stmt).scalars().all()
            filter_conditions.append(OrganizationHistory.id.in_(results))
        if "name" in conditions:
            filter_conditions.append(OrganizationHistory.data["name"].astext == conditions["name"])
        if "part_of" in conditions:
            filter_conditions.append(
                OrganizationHistory.data["partOf"]["reference"].astext == "Organization/" + conditions["part_of"]) # type: ignore

        # sort so that the latest history is first
        stmt = stmt.where(and_(*filter_conditions)).order_by(
            OrganizationHistory.created_at.desc())
        return self.db_session.session.execute(stmt).scalars().all()
