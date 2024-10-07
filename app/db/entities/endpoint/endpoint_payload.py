from uuid import UUID

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.value_sets.endpoint_payload_types import EndpointPayloadType


class EndpointPayload(CommonMixin, Base):
    __tablename__ = "endpoint_payloads"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    endpoint_id: Mapped[UUID] = mapped_column(ForeignKey("endpoints.id"))
    payload_type: Mapped[str] = mapped_column(ForeignKey("endpoint_payload_types.code"))
    mime_type: Mapped[str | None] = mapped_column("mime_type", Text)

    payload: Mapped["EndpointPayloadType"] = relationship(lazy="selectin")
