from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import String, ForeignKey, Text, PrimaryKeyConstraint, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.endpoint.endpoint_contact_point import EndpointContactPoint
from app.db.entities.endpoint.endpoint_payload import EndpointPayload
from app.db.entities.endpoint.endpoint_environment import EndpointEnvironment
from app.db.entities.endpoint.endpoint_header import EndpointHeader
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.organization import organization
from app.db.entities.value_sets.connection_type import ConnectionType
from app.db.entities.value_sets.status import Status


class Endpoint(CommonMixin, Base):
    __tablename__ = "endpoints"
    __table_args__ = (PrimaryKeyConstraint("id"),)

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
    payload: Mapped[Optional[List["EndpointPayload"]]] = relationship(lazy="selectin")
