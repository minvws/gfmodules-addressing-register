from typing import List

from sqlalchemy.orm import Mapped, relationship

from app.db.entities.base import Base
from app.db.entities.endpoint.endpoint_connection_type import EndpointConnectionType
from app.db.entities.mixin.value_set_mixin import ValueSetMixin


class ConnectionType(ValueSetMixin, Base):
    __tablename__ = "connection_types"

    endpoints: Mapped[List["EndpointConnectionType"]] = relationship(
        back_populates="connection"
    )
