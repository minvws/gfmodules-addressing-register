from typing import List
from uuid import UUID, uuid4

from sqlalchemy import types, Integer, ForeignKey, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.contact_point.contact_point_period import ContactPointPeriod
from app.db.entities.endpoint.endpoint_contact_point import EndpointContactPoint
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.value_sets.contact_point_system import ContactPointSystem
from app.db.entities.value_sets.contact_point_use import ContactPointUse


class ContactPoint(CommonMixin, Base):
    __tablename__ = "contact_points"

    __table_args__ = CheckConstraint("rank > 0", name="positive_rank_check")

    id: Mapped[UUID] = mapped_column(
        "id",
        types.Uuid,
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    value: Mapped[str] = mapped_column("value", String, nullable=False)
    rank: Mapped[int] = mapped_column("rank", Integer)
    system_type: Mapped[str] = mapped_column(ForeignKey("contact_point_systems.code"))
    use_type: Mapped[str] = mapped_column(ForeignKey("contact_point_use.code"))

    system: Mapped["ContactPointSystem"] = relationship(back_populates="contact_points")
    period: Mapped["ContactPointPeriod"] = relationship(back_populates="contact_point")
    use: Mapped["ContactPointUse"] = relationship(back_populates="contact_points")
    endpoints: Mapped[List["EndpointContactPoint"]] = relationship(
        back_populates="contact_point"
    )
