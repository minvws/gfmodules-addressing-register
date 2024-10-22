from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.entities.base import Base
from app.db.entities.mixin.history_mixin import HistoryMixin


class OrganizationHistory(HistoryMixin, Base):

    __tablename__ = "organizations_history"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    organization_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"))
    ura_number: Mapped[str] = mapped_column("ura_number", String, nullable=False)
