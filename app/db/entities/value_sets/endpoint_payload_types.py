from typing import List
from sqlalchemy.orm import Mapped, relationship
from app.db.entities.base import Base
from app.db.entities.endpoint.endpoint_payload import EndpointPayload
from app.db.entities.mixin.value_set_mixin import ValueSetMixin


class EndpointPayloadType(ValueSetMixin, Base):
    __tablename__ = "endpoint_payload_types"

    endpoints: Mapped[List["EndpointPayload"]] = relationship(back_populates="payload")
