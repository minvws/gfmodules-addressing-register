from sqlalchemy.orm import Mapped, relationship

from app.db.entities.base import Base
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.entities.mixin.value_set_mixin import ValueSetMixin


class Status(ValueSetMixin, Base):
    __tablename__ = "statuses"

    endpoint: Mapped["Endpoint"] = relationship(back_populates="status")
