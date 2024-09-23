from app.db.entities.mixin.value_set_mixin import ValueSetMixin
from app.db.entities.base import Base


class OrganizationAffiliationRole(ValueSetMixin, Base):
    __tablename__ = "organization_affiliation_roles"
