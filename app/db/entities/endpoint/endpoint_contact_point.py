from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.contact_point.contact_point import ContactPoint
from app.db.entities.mixin.common_mixin import CommonMixin


class EndpointContactPoint(CommonMixin, Base):
    __tablename__ = "endpoints_contact_points"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        UniqueConstraint("endpoint_id", "contact_point_id"),
    )

    endpoint_id: Mapped[UUID] = mapped_column(ForeignKey("endpoints.id"))
    contact_point_id: Mapped[UUID] = mapped_column(ForeignKey("contact_points.id"))

    contact_point: Mapped["ContactPoint"] = relationship(lazy="selectin")
