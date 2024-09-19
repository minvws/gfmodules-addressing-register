from app.db.entities.base import Base
from app.db.entities.mixin.value_set_mixin import ValueSetMixin


class EndpointPayloadType(ValueSetMixin, Base):
    __tablename__ = "endpoint_payload_types"
