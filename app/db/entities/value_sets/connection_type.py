from app.db.entities.base import Base
from app.db.entities.mixin.value_set_mixin import ValueSetMixin


class ConnectionType(ValueSetMixin, Base):
    __tablename__ = "connection_types"
