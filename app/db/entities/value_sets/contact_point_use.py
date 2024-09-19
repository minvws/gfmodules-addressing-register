from app.db.entities.base import Base
from app.db.entities.mixin.value_set_mixin import ValueSetMixin


class ContactPointUse(ValueSetMixin, Base):
    __tablename__ = "contact_point_use"
