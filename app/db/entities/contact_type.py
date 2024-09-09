from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import types, String, TIMESTAMP
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.db.entities.base import Base
from app.db.entities.organization_contact import OrganizationContact


class ContactType(Base):
    """
    Represents a contact type FHIR definition. see: https://terminology.hl7.org/5.1.0/ValueSet-contactentity-type.html
    """

    __tablename__ = "contact_types"

    id: Mapped[UUID] = mapped_column("id", types.UUID, primary_key=True)
    code: Mapped[str] = mapped_column("code", String(10), nullable=False)
    definition: Mapped[str] = mapped_column("definition", String(255), nullable=False)
    display: Mapped[str] = mapped_column("display", String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", TIMESTAMP, nullable=False, default=datetime.now()
    )
    modified_at: Mapped[datetime] = mapped_column(
        "modified_at", TIMESTAMP, nullable=False, default=datetime.now()
    )

    organizations: Mapped[List["OrganizationContact"]] = relationship(
        back_populates="contact_type"
    )
