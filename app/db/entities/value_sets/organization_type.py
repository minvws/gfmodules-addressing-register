from typing import List

from sqlalchemy.orm import Mapped, relationship

from app.db.entities.base import Base
from app.db.entities.mixin.value_set_mixin import ValueSetMixin
from app.db.entities.organization.organization_type_association import (
    OrganizationTypeAssociation,
)


class OrganizationType(ValueSetMixin, Base):
    """
    Represents a Organization Type FHIR definition. See: https://hl7.org/fhir/valueset-organization-type.html
    """

    __tablename__ = "organization_type"

    organizations: Mapped[List["OrganizationTypeAssociation"]] = relationship(
        back_populates="institution_type"
    )
