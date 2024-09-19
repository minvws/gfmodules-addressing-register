from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint, ForeignKey, types
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.organization.organization import Organization
from app.db.entities.value_sets.organization_type import OrganizationType


class OrganizationTypeAssociation(CommonMixin, Base):
    """
    Association object between Organization and InstitutionType (OrganizationType).
    """

    __tablename__ = "organization_type_associations"
    __table_args__ = (PrimaryKeyConstraint("organization_id", "organization_type_id"),)

    id: Mapped[UUID] = mapped_column("id", types.UUID, unique=True)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False
    )
    organization_type: Mapped[str] = mapped_column(
        ForeignKey("organization_types.code"), nullable=False
    )

    organization: Mapped[Organization] = relationship(back_populates="type")
    institution_type: Mapped["OrganizationType"] = relationship(
        back_populates="organizations"
    )
