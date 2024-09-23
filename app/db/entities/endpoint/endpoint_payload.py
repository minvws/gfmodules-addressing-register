from uuid import UUID, uuid4

from sqlalchemy import types, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin

class EndpointPayload(CommonMixin, Base):
    __tablename__ = "endpoint_payloads"

    id: Mapped[UUID] = mapped_column(
        "id",
        types.Uuid,
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    endpoint_id: Mapped[UUID] = mapped_column(ForeignKey("endpoints.id"))
    payload_type: Mapped[str] = mapped_column(ForeignKey("endpoint_payload_types.code"))
