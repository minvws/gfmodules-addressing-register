from app.db.entities.mixin.value_set_mixin import ValueSetMixin
from app.db.entities.base import Base


class AffiliationRole(ValueSetMixin, Base):
    __tablename__ = "affiliation_roles"
