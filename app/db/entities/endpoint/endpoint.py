from sqlalchemy import PrimaryKeyConstraint

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin


class Endpoint(CommonMixin, Base):
    __tablename__ = "endpoints"
    __table_args__ = (PrimaryKeyConstraint("id"),)
