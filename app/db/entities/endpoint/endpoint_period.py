from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.mixin.period_mixin import PeriodMixin
from app.db.entities.endpoint import endpoint


class EndpointPeriod(PeriodMixin, Base):
    __tablename__ = "endpoint_periods"

    endpoint_id: Mapped[UUID] = mapped_column(ForeignKey("endpoints.id"), unique=True)

    endpoint: Mapped["endpoint.Endpoint"] = relationship(back_populates="period")
