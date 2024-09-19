from uuid import UUID, uuid4

from sqlalchemy import PrimaryKeyConstraint, ForeignKey, types
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.value_sets.connection_type import ConnectionType
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.entities.mixin.common_mixin import CommonMixin


class EndpointConnectionType(CommonMixin, Base):
    __tablename__ = "endpoints_connection_types"
    __table_arg__ = (PrimaryKeyConstraint("endpoint_id", "connection_type_id"),)

    id: Mapped[UUID] = mapped_column(
        "id",
        types.Uuid,
        nullable=False,
        default=uuid4,
    )
    endpoint_id: Mapped[UUID] = mapped_column(ForeignKey("endpoints.id"))
    connection_type: Mapped[str] = mapped_column(ForeignKey("connection_types.code"))

    endpoint: Mapped["Endpoint"] = relationship("connection_type")
    connection: Mapped["ConnectionType"] = relationship("endpoints")
