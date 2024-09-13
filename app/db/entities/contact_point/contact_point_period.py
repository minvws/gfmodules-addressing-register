from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.contact_point.contact_point import ContactPoint
from app.db.entities.mixin.period_mixin import PeriodMixin


class ContactPointPeriod(PeriodMixin, Base):
    __tablename__ = "contact_point_periods"

    contact_point_id: Mapped[UUID] = mapped_column(
        ForeignKey("contact_points.id"), unique=True
    )

    contact_point: Mapped["ContactPoint"] = relationship(back_populates="period")
