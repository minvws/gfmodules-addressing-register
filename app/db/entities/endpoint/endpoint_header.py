from uuid import UUID, uuid4

from sqlalchemy import types, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin


class EndpointHeader(CommonMixin, Base):
    __tablename__ = "endpoint_headers"
    id: Mapped[UUID] = mapped_column(
        "id",
        types.Uuid,
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    data: Mapped[str] = mapped_column("data", Text)
    endpoint_id: Mapped[UUID] = mapped_column(ForeignKey("endpoints.id"))
