from uuid import UUID

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.value_sets.environment import Environment
from app.db.entities.mixin.common_mixin import CommonMixin


class EndpointEnvironment(CommonMixin, Base):
    __tablename__ = "endpoints_environments"
    __table_args__ = (PrimaryKeyConstraint("endpoint_id", "environment_type"),)

    endpoint_id: Mapped[UUID] = mapped_column(
        ForeignKey("endpoints.id"), primary_key=True
    )
    environment_type: Mapped[str] = mapped_column(
        ForeignKey("environments.code"), primary_key=True
    )

    environment: Mapped["Environment"] = relationship()
