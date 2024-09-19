from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.entities.base import Base
from app.db.entities.mixin.period_mixin import PeriodMixin


class EndpointPeriod(PeriodMixin, Base):
    __tablename__ = "endpoint_periods"

    endpoint_id: Mapped[UUID] = mapped_column(ForeignKey("endpoints.id"), unique=True)
