from sqlalchemy import PrimaryKeyConstraint

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin


class OrganizationAffiliation(CommonMixin, Base):
    __tablename__ = "organization_affiliations"
    __table_args__ = (PrimaryKeyConstraint("id"),)

