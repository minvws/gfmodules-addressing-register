from sqlalchemy import PrimaryKeyConstraint

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin


class Location(CommonMixin, Base):
    __tablename__ = "locations"
    __table_args__ = (PrimaryKeyConstraint("id"),)
