from typing import List

from sqlalchemy.orm import Mapped, relationship

from app.db.entities.base import Base
from app.db.entities.mixin.value_set_mixin import ValueSetMixin
from app.db.entities.organization.organization_contact import OrganizationContact


class ContactType(ValueSetMixin, Base):
    """
    Represents a contact type FHIR definition. see: https://terminology.hl7.org/5.1.0/ValueSet-contactentity-type.html
    """

    __tablename__ = "contact_types"

    organizations: Mapped[List["OrganizationContact"]] = relationship(
        back_populates="contact"
    )
