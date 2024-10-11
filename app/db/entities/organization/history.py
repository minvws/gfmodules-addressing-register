from uuid import UUID

from sqlalchemy import types, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.entities.mixin.history_mixin import HistoryMixin


class OrganizaitonHistory(HistoryMixin):

    __tablename__ = "organization_history"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    organization_id: Mapped[UUID] = mapped_column("organization_id", types.UUID)
