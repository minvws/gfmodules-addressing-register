from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.entities.base import Base
from app.db.entities.mixin.period_mixin import PeriodMixin


class ContactPointPeriod(PeriodMixin, Base):
    __tablename__ = "contact_point_periods"

    contact_point_id: Mapped[UUID] = mapped_column(
        ForeignKey("contact_points.id"), unique=True
    )
