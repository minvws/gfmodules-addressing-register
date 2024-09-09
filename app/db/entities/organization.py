from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import types, Boolean, String, Text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.organization_type_association import OrganizationTypeAssociation
from app.db.entities.organization_contact import OrganizationContact


class Organization(Base):
    """
    Representation of a FHIR Organization definition. see: https://hl7.org/fhir/organization.html
    """

    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column("id", types.UUID, primary_key=True)
    active: Mapped[bool] = mapped_column(
        "active", Boolean, default=True, nullable=False
    )
    name: Mapped[str] = mapped_column("name", String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column("description", Text)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", TIMESTAMP, nullable=False, default=datetime.now()
    )
    modified_at: Mapped[datetime] = mapped_column(
        "modified_at", TIMESTAMP, nullable=False, default=datetime.now()
    )

    part_of: Mapped["Organization"] = relationship(remote_side=[id])
    type: Mapped[List["OrganizationTypeAssociation"]] = relationship(
        back_populates="organization_type"
    )
    contact: Mapped[List["OrganizationContact"]] = relationship(
        back_populates="organization"
    )
