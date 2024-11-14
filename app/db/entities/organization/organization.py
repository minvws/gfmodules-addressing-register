from sqlalchemy import String, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin


class Organization(CommonMixin, Base):
    """
    Representation of a FHIR Organization definition. see: https://hl7.org/fhir/organization.html
    """

    __tablename__ = "organizations"
    __table_args__ = (PrimaryKeyConstraint("id"),)
    ura_number: Mapped[str] = mapped_column("ura_number", String, unique=True)
