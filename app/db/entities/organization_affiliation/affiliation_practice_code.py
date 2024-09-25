from uuid import UUID
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.value_sets.practice_code import PracticeCode


class AffiliationPracticeCode(CommonMixin, Base):
    __tablename__ = "organization_affiliation_practice_codes"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    affiliation_id: Mapped[UUID] = mapped_column(
        ForeignKey("organization_affiliations.id")
    )
    practice_code: Mapped[str] = mapped_column(ForeignKey("practice_codes.code"))

    code: Mapped["PracticeCode"] = relationship()
