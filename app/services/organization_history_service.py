from datetime import datetime
from typing import Literal, Sequence
from uuid import UUID

from app.db.db import Database
from app.db.entities.organization.history import OrganizationHistory
from app.db.entities.organization.organization import Organization
from app.db.repositories.organization_history_repository import OrganizationHistoryRepository
from app.mappers.fhir_mapper import map_to_fhir_organization


class OrganizationHistoryService:
    def __init__(self, database: Database):
        self.database = database

    def create(self, organization: Organization, interaction: Literal["create", "update", "delete"]) -> None:
        with self.database.get_db_session() as session:

            if interaction == "delete":
                print("Deleting organization")

            repository = session.get_repository(OrganizationHistoryRepository)

            fhir_org = map_to_fhir_organization(organization, True)

            history = OrganizationHistory(
                organization_id=organization.id,
                ura_number=organization.ura_number,
                interaction=interaction,
                data=fhir_org.dict()
            )
            repository.create(history)

    def find(self,
             id: UUID | None = None,
             organization_id: UUID | None = None,
             identifier: str | None = None,
             active: bool | None = None,
             endpoint_id: UUID | None = None,
             name: str | None = None,
             part_of: UUID | None = None,
             since: datetime | None = None,
             updated_at: datetime | None = None
             ) -> Sequence[OrganizationHistory]:
        params = {
            "id": id,
            "organization_id": organization_id,
            "identifier": identifier,
            "active": active,
            "endpoint_id": endpoint_id,
            "name": name,
            "part_of": part_of,
            "since": since,
            "updated_at": updated_at
        }
        filtered_params = {k: v for k, v in params.items() if v is not None}
        with self.database.get_db_session() as session:
            organization_history_repository = session.get_repository(OrganizationHistoryRepository)
            return organization_history_repository.find(**filtered_params)
