from datetime import datetime
from uuid import UUID

from sqlalchemy import types, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.organization import Organization
from app.db.entities.contact_type import ContactType


class OrganizationContact(Base):
    """
    Association object between Organization and ContactType.
    """

    __tablename__ = "organization_contacts"

    id: Mapped[UUID] = mapped_column("id", types.UUID, unique=True)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False
    )
    contact_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("contact_types.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        "created_at", TIMESTAMP, nullable=False, default=datetime.now()
    )
    modified_at: Mapped[datetime] = mapped_column(
        "modified_at", TIMESTAMP, nullable=False, default=datetime.now()
    )

    organization: Mapped["Organization"] = relationship(back_populates="contact")
    contact_type: Mapped["ContactType"] = relationship(back_populates="organizations")
