import logging
from datetime import datetime
from typing import Sequence, Any, Dict
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, literal_column, or_, cast, TIMESTAMP
from sqlalchemy.exc import DatabaseError

from app.db.decorator import repository
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.repositories.repository_base import RepositoryBase
from app.services.utils import update_resource_meta

logger = logging.getLogger(__name__)


@repository(Endpoint)
class EndpointsRepository(RepositoryBase):
    def get_one(self, **kwargs: bool | str | UUID | dict[str, str]) -> Endpoint | None:
        stmt = (
            select(Endpoint)
            .where(
                Endpoint.latest.__eq__(True),
                Endpoint.deleted.__eq__(False),
            )
            .filter_by(**kwargs)
        )
        return self.db_session.session.execute(stmt).scalars().first()

    def get(
        self, **kwargs: bool | str | UUID | dict[str, str] | int
    ) -> Endpoint | None:
        """
        does not apply filters on latest and deleted columns.
        """
        stmt = select(Endpoint).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().first()

    def get_many(
        self, **kwargs: bool | str | UUID | dict[str, str]
    ) -> Sequence[Endpoint]:
        stmt = select(Endpoint).filter_by(**kwargs)
        return self.db_session.session.execute(stmt).scalars().all()

    def find(
        self, **conditions: bool | str | UUID | dict[str, Any] | datetime | None
    ) -> Sequence[Endpoint]:
        stmt = select(Endpoint)
        filter_conditions: list[Any] = []

        if "latest" in conditions and conditions["latest"] is True:
            filter_conditions.append(Endpoint.latest)
            filter_conditions.append(Endpoint.deleted.__eq__(False))

        if "id" in conditions:
            filter_conditions.append(Endpoint.fhir_id == conditions["id"])

        if "connectionType" in conditions:
            filter_conditions.append(
                Endpoint.data["connectionType"]["code"].astext
                == conditions["connectionType"]
            )

        if "identifier" in conditions:
            stmt = stmt.select_from(
                Endpoint,
                func.jsonb_array_elements(Endpoint.data["identifier"]).alias(
                    "identifier"
                ),
            ).where(literal_column("identifier->>'value'") == conditions["identifier"])

        if "name" in conditions:
            filter_conditions.append(
                Endpoint.data["name"].astext.like(f'%{conditions["name"]}%')
            )

        if "managingOrganization" in conditions:
            filter_conditions.append(
                Endpoint.data["managingOrganization"]["reference"].astext
                == conditions["managingOrganization"]
            )

        if "payloadType" in conditions:
            stmt = (
                stmt.select_from(
                    Endpoint,
                    func.jsonb_array_elements(Endpoint.data["payloadType"]).alias(
                        "payload_type"
                    ),
                )
                .select_from(
                    func.jsonb_array_elements(
                        literal_column("payload_type->'coding'")
                    ).alias("coding")
                )
                .where(
                    or_(
                        literal_column("coding->>'system'").ilike(
                            f"%{conditions['payloadType']}%"
                        ),
                        literal_column("coding->>'code'").ilike(
                            f"%{conditions['payloadType']}%"
                        ),
                    )
                )
            )

        if "status" in conditions:
            filter_conditions.append(
                Endpoint.data["status"].astext == conditions["status"]
            )

        if "sort_history" in conditions and conditions["sort_history"] is True:
            # sorted with oldest versions last
            stmt = stmt.order_by(cast(Endpoint.data['meta']['lastUpdated'].astext, TIMESTAMP(timezone=True)).desc(), Endpoint.version.desc())

        if "since" in conditions:
            filter_conditions.append(
                cast(Endpoint.data['meta']['lastUpdated'].astext, TIMESTAMP(timezone=True)) >= conditions["since"]
            )

        stmt = stmt.where(*filter_conditions)

        return self.db_session.session.execute(stmt).scalars().all()

    def create(self, endpoint: Endpoint) -> Endpoint:
        try:
            update_resource_meta(endpoint, method="create")
            self.db_session.add(endpoint)
            self.db_session.commit()
            return endpoint
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to add Endpoint {endpoint.id}: {e}")
            raise e

    def delete(self, endpoint: Endpoint) -> None:
        try:
            self._update_entry_latest(endpoint)
            updated_endpoint = Endpoint(
                fhir_id=endpoint.fhir_id,
                version=endpoint.version,
                data=None,
            )
            update_resource_meta(updated_endpoint, method="delete")

            self.db_session.add(updated_endpoint)
            self.db_session.commit()
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to delete Endpoint {endpoint.id}: {e}")
            raise e

    def update(self, endpoint: Endpoint, fhir_data: Dict[str, Any]) -> Endpoint:
        try:
            self._update_entry_latest(endpoint)
            updated_endpoint = Endpoint(
                fhir_id=endpoint.fhir_id,
                version=endpoint.version,
                data=jsonable_encoder(fhir_data),
            )
            update_resource_meta(updated_endpoint, method="update")

            self.db_session.add(updated_endpoint)
            self.db_session.commit()
            return updated_endpoint
        except DatabaseError as e:
            self.db_session.rollback()
            logging.error(f"Failed to update Endpoint {endpoint.id}: {e}")
            raise e

    def _update_entry_latest(self, endpoint: Endpoint) -> None:
        (
            self.db_session.query(Endpoint)
            .filter(Endpoint.fhir_id == endpoint.fhir_id, Endpoint.latest)
            .update({Endpoint.latest: False})
        )
