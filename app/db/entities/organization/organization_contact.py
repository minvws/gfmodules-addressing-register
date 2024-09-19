from uuid import UUID

from sqlalchemy import types, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.value_sets.contact_type import ContactType
from app.db.entities.organization.organization import Organization


class OrganizationContact(CommonMixin, Base):
    """
    Association object between Organization and ContactType.
    """

    __tablename__ = "organization_contacts"

    id: Mapped[UUID] = mapped_column("id", types.UUID, unique=True)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False
    )
    contact_type: Mapped[str] = mapped_column(
        ForeignKey("contact_types.code"), nullable=False
    )

    organization: Mapped["Organization"] = relationship(back_populates="contact")
    contact: Mapped["ContactType"] = relationship(back_populates="organizations")
