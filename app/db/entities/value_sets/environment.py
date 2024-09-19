from typing import List

from sqlalchemy.orm import Mapped, relationship

from app.db.entities.base import Base
from app.db.entities.endpoint.endpoint_environment import EndpointEnvironment
from app.db.entities.mixin.value_set_mixin import ValueSetMixin


class Environment(ValueSetMixin, Base):
    __tablename__ = "environments"

    endpoints: Mapped[List["EndpointEnvironment"]] = relationship(
        back_populates="environment"
    )
