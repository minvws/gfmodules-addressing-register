from sqlalchemy import PrimaryKeyConstraint

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin


class PractitionerRole(CommonMixin, Base):
    __tablename__ = "practitioner_roles"
    __table_args__ = (PrimaryKeyConstraint("id"),)
