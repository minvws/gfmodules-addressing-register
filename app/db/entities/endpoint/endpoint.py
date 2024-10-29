from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import String, ForeignKey, Text, PrimaryKeyConstraint, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data import EndpointStatus
from app.db.entities.base import Base
from app.db.entities.endpoint.endpoint_contact_point import EndpointContactPoint
from app.db.entities.endpoint.endpoint_environment import EndpointEnvironment
from app.db.entities.endpoint.endpoint_header import EndpointHeader
from app.db.entities.endpoint.endpoint_payload import EndpointPayload
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.organization import organization
from app.db.entities.value_sets.connection_type import ConnectionType
from app.db.entities.value_sets.endpoint_payload_types import EndpointPayloadType
from app.db.entities.value_sets.status import Status
from app.data import ConnectionType as ConnectionTypeEnum


class Endpoint(CommonMixin, Base):
    __tablename__ = "endpoints"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    identifier: Mapped[str | None] = mapped_column("identifier", String, unique=True)
    name: Mapped[str | None] = mapped_column("name", String(150))
    description: Mapped[str | None] = mapped_column("description", String)
    address: Mapped[str] = mapped_column("address", Text)
    organization_id: Mapped[UUID | None] = mapped_column(ForeignKey("organizations.id"))
    status_type: Mapped[str] = mapped_column(
        ForeignKey("statuses.code"), nullable=False
    )
    connection_type: Mapped[str] = mapped_column(
        ForeignKey("connection_types.code"), nullable=False
    )
    period_start_date: Mapped[datetime | None] = mapped_column(
        "period_start_date", TIMESTAMP
    )
    period_end_date: Mapped[datetime | None] = mapped_column(
        "period_end_date", TIMESTAMP
    )

    managing_organization: Mapped[Optional["organization.Organization"]] = relationship(
        back_populates="endpoints", lazy="selectin"
    )
    status: Mapped["Status"] = relationship(lazy="selectin")
    connection: Mapped["ConnectionType"] = relationship(lazy="selectin")
    headers: Mapped[List["EndpointHeader"]] = relationship(lazy="selectin")
    environment_type: Mapped[Optional[List["EndpointEnvironment"]]] = relationship()
    contacts: Mapped[Optional[List["EndpointContactPoint"]]] = relationship(
        lazy="selectin"
    )
    payload: Mapped[List["EndpointPayload"]] = relationship(
        lazy="selectin", cascade="all, delete-orphan"
    )

    @staticmethod
    def create_instance(address: str,
                        status_type: EndpointStatus,
                        connection_type: ConnectionTypeEnum,
                        payload_type: EndpointPayloadType,
                        name: str | None = None,
                        payload_mime_type: str | None = None,
                        managing_organization: organization.Organization | None = None,
                        identifier: str | None = None,
                        description: str | None = None) -> "Endpoint":
        new_endpoint = Endpoint(
            address=address,
            status_type=str(status_type),
            connection_type=str(connection_type),
            identifier=identifier,
            managing_organization=managing_organization,
            description=description,
            name=name,
        )
        endpoint_payload = EndpointPayload(
            endpoint_id=new_endpoint.id,
            payload_type=payload_type.code,
            mime_type=payload_mime_type,
            payload = payload_type
        )
        new_endpoint.payload.append(endpoint_payload)
        return new_endpoint


