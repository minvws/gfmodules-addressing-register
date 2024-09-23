from typing import Optional, List
from uuid import UUID

from sqlalchemy import types, Boolean, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.endpoint import endpoint
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.organization.organization_type_association import (
    OrganizationTypeAssociation,
)
from app.db.entities.organization.organization_contact import OrganizationContact


class Organization(CommonMixin, Base):
    """
    Representation of a FHIR Organization definition. see: https://hl7.org/fhir/organization.html
    """

    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column("id", types.UUID, primary_key=True)
    ura_number: Mapped[str] = mapped_column("ura_number", String, unique=True)
    active: Mapped[bool] = mapped_column(
        "active", Boolean, default=True, nullable=False
    )
    parent_organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column("name", String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column("description", Text)

    part_of: Mapped["Organization"] = relationship(remote_side=[id])
    type: Mapped[List["OrganizationTypeAssociation"]] = relationship(
    )
    contact: Mapped[List["OrganizationContact"]] = relationship(
    )
    endpoints: Mapped[List["endpoint.Endpoint"]] = relationship(back_populates="managing_organization")
