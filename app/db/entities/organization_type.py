from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import types, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.organization_type_association import OrganizationTypeAssociation


class OrganizationType(Base):
    """
    Represents a Organization Type FHIR definition. See: https://hl7.org/fhir/valueset-organization-type.html
    """

    __tablename__ = "organization_type"

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

    organizations: Mapped[List["OrganizationTypeAssociation"]] = relationship(
        back_populates="institution_type"
    )
