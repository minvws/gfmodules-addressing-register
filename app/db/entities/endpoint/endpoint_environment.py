from uuid import UUID, uuid4

from sqlalchemy import types, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.entities.value_sets.environment import Environment
from app.db.entities.mixin.common_mixin import CommonMixin


class EndpointEnvironment(CommonMixin, Base):
    __tablename__ = "endpoints_environments"

    id: Mapped[UUID] = mapped_column(
        "id",
        types.Uuid,
        nullable=False,
        default=uuid4,
    )
    endpoint_id: Mapped[UUID] = mapped_column(ForeignKey("endpoints.id"))
    environment_type: Mapped[str] = mapped_column(ForeignKey("environments.code"))

    endpoint: Mapped["Endpoint"] = relationship(back_populates="environment_type")
    environment: Mapped["Environment"] = relationship(back_populates="endpoints")
