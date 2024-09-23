

from app.db.entities.base import Base
from app.db.entities.mixin.value_set_mixin import ValueSetMixin


class OrganizationType(ValueSetMixin, Base):
    """
    Represents a Organization Type FHIR definition. See: https://hl7.org/fhir/valueset-organization-type.html
    """

    __tablename__ = "organization_types"
