from uuid import UUID

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.value_sets.connection_type import ConnectionType
from app.db.entities.mixin.common_mixin import CommonMixin


class EndpointConnectionType(CommonMixin, Base):
    __tablename__ = "endpoints_connection_types"
    __table_args__ = (PrimaryKeyConstraint("endpoint_id", "connection_type"),)

    endpoint_id: Mapped[UUID] = mapped_column(
        ForeignKey("endpoints.id"), primary_key=True
    )
    connection_type: Mapped[str] = mapped_column(
        ForeignKey("connection_types.code"), primary_key=True
    )

    connection: Mapped["ConnectionType"] = relationship()
