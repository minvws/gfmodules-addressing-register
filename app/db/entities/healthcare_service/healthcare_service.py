from sqlalchemy import PrimaryKeyConstraint

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin


class HealthcareService(CommonMixin, Base):
    __tablename__ = "healthcare_services"
    __table_args__ = (PrimaryKeyConstraint("id"),)
