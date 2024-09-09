from datetime import datetime
from uuid import UUID

from sqlalchemy import TIMESTAMP, PrimaryKeyConstraint, ForeignKey, types
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.organization_type import OrganizationType
from app.db.entities.organization import Organization


class OrganizationTypeAssociation(Base):
    """
    Association object between Organization and InstitutionType (OrganizationType).
    """

    __tablename__ = "organization_type_associations"
    __table_args__ = (PrimaryKeyConstraint("organization_id", "organization_type_id"),)

    id: Mapped[UUID] = mapped_column("id", types.UUID, unique=True)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False
    )
    organization_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("institution_types.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        "created_at", TIMESTAMP, nullable=False, default=datetime.now()
    )
    modified_at: Mapped[datetime] = mapped_column(
        "modified_at", TIMESTAMP, nullable=False, default=datetime.now()
    )

    organization: Mapped["Organization"] = relationship(back_populates="type")
    institution_type: Mapped["OrganizationType"] = relationship(
        back_populates="organizations"
    )
