from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import types, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.endpoint.endpoint_contact_point import EndpointContactPoint
from app.db.entities.endpoint.endpoint_payload import EndpointPayload
from app.db.entities.endpoint.endpoint_period import EndpointPeriod
from app.db.entities.endpoint.endpoint_connection_type import EndpointConnectionType
from app.db.entities.endpoint.endpoint_environment import EndpointEnvironment
from app.db.entities.endpoint.endpoint_header import EndpointHeader
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.organization import organization
from app.db.entities.value_sets.status import Status


class Endpoint(CommonMixin, Base):
    __tablename__ = "endpoints"

    id: Mapped[UUID] = mapped_column(
        "id",
        types.Uuid,
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    name: Mapped[str | None] = mapped_column("name", String(150))
    description: Mapped[str | None] = mapped_column("description", String)
    address: Mapped[str] = mapped_column("address", Text)
    organization_id: Mapped[UUID | None] = mapped_column(ForeignKey("organizations.id"))
    status_type: Mapped[str] = mapped_column(
        ForeignKey("statuses.code"), nullable=False
    )

    status: Mapped["Status"] = relationship(back_populates="endpoint")
    connection_type: Mapped[List["EndpointConnectionType"]] = relationship(
        back_populates="endpoint"
    )
    managing_organization: Mapped[Optional["organization.Organization"]] = relationship(
        back_populates="endpoints"
    )
    period: Mapped[Optional["EndpointPeriod"]] = relationship(back_populates="endpoint")
    headers: Mapped[List["EndpointHeader"]] = relationship(back_populates="endpoint")
    environment_type: Mapped[Optional[List["EndpointEnvironment"]]] = relationship(
        back_populates="endpoint"
    )
    contact: Mapped[Optional[List["EndpointContactPoint"]]] = relationship(
        back_populates="endpoint"
    )
    payload: Mapped[Optional[List["EndpointPayload"]]] = relationship(
        back_populates="endpoint"
    )
