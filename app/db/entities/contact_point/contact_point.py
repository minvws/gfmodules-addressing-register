from datetime import datetime

from sqlalchemy import (
    Integer,
    ForeignKey,
    String,
    CheckConstraint,
    PrimaryKeyConstraint,
    TIMESTAMP,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.value_sets.contact_point_system import ContactPointSystem
from app.db.entities.value_sets.contact_point_use import ContactPointUse


class ContactPoint(CommonMixin, Base):
    __tablename__ = "contact_points"

    __table_args__ = (
        PrimaryKeyConstraint("id"),
        CheckConstraint("rank > 0", name="positive_rank_check"),
    )

    value: Mapped[str] = mapped_column("value", String, nullable=False)
    rank: Mapped[int] = mapped_column("rank", Integer)
    system_type: Mapped[str] = mapped_column(ForeignKey("contact_point_systems.code"))
    use_type: Mapped[str] = mapped_column(ForeignKey("contact_point_use.code"))
    period_start_date: Mapped[datetime | None] = mapped_column(
        "period_start_date", TIMESTAMP
    )
    period_end_date: Mapped[datetime | None] = mapped_column(
        "period_end_date", TIMESTAMP
    )

    system: Mapped["ContactPointSystem"] = relationship(lazy="selectin")
    use: Mapped["ContactPointUse"] = relationship(lazy="selectin")
