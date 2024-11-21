import logging
from datetime import datetime
from typing import Sequence, Any, Dict
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, Boolean, or_, func, literal_column
from sqlalchemy.exc import DatabaseError

from app.db.decorator import repository
from app.db.entities.organization.organization import Organization
from app.db.repositories.repository_base import RepositoryBase
from app.services.utils import update_resource_meta

logger = logging.getLogger(__name__)


@repository(Organization)
class OrganizationsRepository(RepositoryBase):
    def get_one(
        self, **kwargs: bool|str|UUID|dict[str, str]
    ) -> Organization | None:
        stmt = (
            select(Organization)
            .where(Organization.latest.__eq__(True), Organization.deleted.__eq__(False))
            .filter_by(**kwargs)
        )
        return self.db_session.session.execute(stmt).scalars().first()

    def get(
        self, **kwargs: bool|str|UUID|dict[str, str]|int
    ) -> Organization | None:
        """
        does not apply filters on latest and deleted columns.
        """
        stmt = select(Organization).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().first()

    def get_many(
        self, **kwargs: bool|str|UUID|dict[str, str]
    ) -> Sequence[Organization]:
        stmt = select(Organization).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().all()

    def find(
        self, **conditions: bool|str|UUID|dict[str, Any]|None|datetime
    ) -> Sequence[Organization]:
        stmt = select(Organization)
        filter_conditions: list[Any] = []

        conditions = {k: v for k, v in conditions.items() if v is not None}

        stmt = self._add_address_filter_conditions(stmt, **conditions)

        if "latest" in conditions and conditions["latest"] is True:
            filter_conditions.append(Organization.latest)
            filter_conditions.append(Organization.deleted.is_(False))

        if "id" in conditions:
            filter_conditions.append(Organization.fhir_id == conditions["id"])

        if "active" in conditions:
            filter_conditions.append(
                Organization.data["active"].astext.cast(Boolean) == conditions["active"]
            )

        if "endpoint" in conditions:
            filter_conditions.append(
                Organization.data["endpoint"].contains(
                    [{"reference": conditions["endpoint"]}]
                )
            )

        if "identifier" in conditions:
            stmt = stmt.select_from(
                Organization,
                func.jsonb_array_elements(Organization.data["identifier"]).alias(
                    "identifier"
                ),
            ).where(literal_column("identifier->>'value'") == conditions["identifier"])

        if "name" in conditions:
            filter_conditions.append(
                Organization.data["name"].astext.like(f'%{conditions["name"]}%')
            )

        if "part_of" in conditions:
            filter_conditions.append(
                Organization.data["partOf"]["reference"].astext == conditions["part_of"]
            )

        if "phonetic" in conditions:
            filter_conditions.append(
                Organization.data["name"]["phonetic"].astext == conditions["phonetic"]
            )

        if "type" in conditions:
            filter_conditions.append(
                Organization.data["type"].astext == conditions["type"]
            )

        if "sort_history" in conditions and conditions["sort_history"] is True:
            stmt = stmt.order_by( # sorted with oldest versions last
                Organization.modified_at.desc(), Organization.version.desc()
            )

        if "since" in conditions:
            filter_conditions.append(
                # TODO : Filter on meta->>lastUpdated instead
                Organization.modified_at >= conditions["since"],
            )

        stmt = stmt.where(*filter_conditions)
        return self.db_session.session.execute(stmt).scalars().all()

    @staticmethod
    def _add_address_filter_conditions(stmt: Any, **conditions: bool | str | UUID | dict[str, Any]|datetime|None) -> Any:
        if "address" in conditions:
            stmt = stmt.select_from(
                Organization,
                func.jsonb_array_elements(Organization.data["address"]).alias(
                    "address"
                ),
            ).where(
                or_(
                    literal_column("address->>'use'").ilike(
                        f"%{conditions['address']}%"
                    ),
                    literal_column("address->>'city'").ilike(
                        f"%{conditions['address']}%"
                    ),
                    literal_column("address->>'text'").ilike(
                        f"%{conditions['address']}%"
                    ),
                    literal_column("address->>'type'").ilike(
                        f"%{conditions['address']}%"
                    ),
                    literal_column("address->>'state'").ilike(
                        f"%{conditions['address']}%"
                    ),
                    literal_column("address->>'country'").ilike(
                        f"%{conditions['address']}%"
                    ),
                    literal_column("address->>'postalCode'").ilike(
                        f"%{conditions['address']}%"
                    ),
                )
            )

        if "address_city" in conditions:
            stmt = stmt.select_from(
                Organization,
                func.jsonb_array_elements(Organization.data["address"]).alias(
                    "address"
                ),
            ).where(literal_column("address ->> 'city'") == conditions["address_city"])

        if "address_country" in conditions:
            stmt = stmt.select_from(
                Organization,
                func.jsonb_array_elements(Organization.data["address"]).alias(
                    "address"
                ),
            ).where(
                literal_column("address ->> 'country'") == conditions["address_country"]
            )

        if "address_postal_code" in conditions:
            stmt = stmt.select_from(
                Organization,
                func.jsonb_array_elements(Organization.data["address"]).alias(
                    "address"
                ),
            ).where(
                literal_column("address ->> 'postalCode'")
                == conditions["address_postal_code"]
            )

        if "address_state" in conditions:
            stmt = stmt.select_from(
                Organization,
                func.jsonb_array_elements(Organization.data["address"]).alias(
                    "address"
                ),
            ).where(
                literal_column("address ->> 'state'") == conditions["address_state"]
            )

        if "address_use" in conditions:
            stmt = stmt.select_from(
                Organization,
                func.jsonb_array_elements(Organization.data["address"]).alias(
                    "address"
                ),
            ).where(
                literal_column("address ->> 'use'")
                == conditions["address_use"]
            )
        return stmt

    def create(self, organization: Organization) -> Organization:
        try:
            update_resource_meta(organization, method="create")
            self.db_session.add(organization)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add organization {organization.id}: {e}")
            raise e
        return organization

    def delete(self, organization: Organization) -> None:
        try:
            self._update_entry_latest(organization)
            updated_organization = Organization(
                fhir_id=organization.fhir_id,
                ura_number=organization.ura_number,
                data=None,
                version=organization.version,
            )
            update_resource_meta(updated_organization, method="delete")
            self.db_session.add(updated_organization)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to delete organization {organization.id}: {e}")
            raise e

    def update(
        self, organization: Organization, fhir_data: Dict[str, Any]
    ) -> Organization:
        try:
            self._update_entry_latest(organization)
            target_org = Organization(
                fhir_id=organization.fhir_id,
                ura_number=organization.ura_number,
                data=jsonable_encoder(fhir_data),
                version=organization.version,
            )
            update_resource_meta(target_org, method="update")
            self.db_session.add(target_org)
            self.db_session.commit()
            return target_org
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to update organization {organization.id}: {e}")
            raise e

    def _update_entry_latest(self, organization: Organization) -> None:
        (
            self.db_session.query(Organization)
            .filter(Organization.fhir_id == organization.fhir_id, Organization.latest)
            .update({Organization.latest: False})
        )
