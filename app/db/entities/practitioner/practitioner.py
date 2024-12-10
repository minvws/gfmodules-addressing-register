from sqlalchemy import PrimaryKeyConstraint

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin


class Practitioner(CommonMixin, Base):
    __tablename__ = "practitioners"
    __table_args__ = (PrimaryKeyConstraint("id"),)
