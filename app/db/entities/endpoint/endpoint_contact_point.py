from uuid import UUID, uuid4

from sqlalchemy import types, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.contact_point.contact_point import ContactPoint
from app.db.entities.mixin.common_mixin import CommonMixin


class EndpointContactPoint(CommonMixin, Base):
    __tablename__ = "endpoints_contact_points"
    __table_args__ = (UniqueConstraint("endpoint_id", "contact_point_id"),)

    id: Mapped[UUID] = mapped_column(
        "id",
        types.Uuid,
        nullable=False,
        primary_key=True,
        default=uuid4,
    )
    endpoint_id: Mapped[UUID] = mapped_column(ForeignKey("endpoints.id"))
    contact_point_id: Mapped[UUID] = mapped_column(ForeignKey("contact_points.id"))

    contact_point: Mapped["ContactPoint"] = relationship(back_populates="endpoints")
