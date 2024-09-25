from uuid import UUID

from sqlalchemy import Text, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin


class EndpointHeader(CommonMixin, Base):
    __tablename__ = "endpoint_headers"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    data: Mapped[str] = mapped_column("data", Text)
    endpoint_id: Mapped[UUID] = mapped_column(ForeignKey("endpoints.id"))
