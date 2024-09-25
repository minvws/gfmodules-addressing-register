from uuid import UUID

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.value_sets.contact_type import ContactType


class OrganizationContact(CommonMixin, Base):
    """
    Association object between Organization and ContactType.
    """

    __tablename__ = "organization_contacts"
    __table_args__ = (PrimaryKeyConstraint("organization_id", "contact_type"),)

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
    )
    contact_type: Mapped[str] = mapped_column(
        ForeignKey("contact_types.code"),
        nullable=False,
    )

    contact: Mapped["ContactType"] = relationship()
