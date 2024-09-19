from typing import List

from sqlalchemy.orm import Mapped, relationship

from app.db.entities.base import Base
from app.db.entities.contact_point.contact_point import ContactPoint
from app.db.entities.mixin.value_set_mixin import ValueSetMixin


class ContactPointSystem(ValueSetMixin, Base):
    __tablename__ = "contact_point_systems"

    contact_points: Mapped[List["ContactPoint"]] = relationship(back_populates="system")
