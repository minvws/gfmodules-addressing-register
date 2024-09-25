from uuid import UUID

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.value_sets.affiliation_role import AffiliationRole


class OrganizationAffiliationRole(CommonMixin, Base):
    __tablename__ = "organization_affiliation_roles"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    affiliation_id: Mapped[UUID] = mapped_column(
        ForeignKey("organization_affiliations.id")
    )
    role_code: Mapped[str] = mapped_column(ForeignKey("affiliation_roles.code"))

    role: Mapped["AffiliationRole"] = relationship()
