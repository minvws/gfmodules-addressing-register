from datetime import datetime
from typing import Optional, Dict, List, Any
from uuid import UUID

from sqlalchemy import Boolean, TIMESTAMP, JSON, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.organization.organization import Organization
from app.db.entities.organization_affiliation.affiliation_endpoint import (
    AffiliationEndpoint,
)
from app.db.entities.organization_affiliation.affiliation_practice_code import (
    AffiliationPracticeCode,
)
from app.db.entities.organization_affiliation.organization_affiliation_role import (
    OrganizationAffiliationRole,
)


class OrganizationAffiliation(CommonMixin, Base):
    __tablename__ = "organization_affiliations"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    active: Mapped[bool] = mapped_column("active", Boolean, default=True)
    period_start_date: Mapped[Optional[datetime]] = mapped_column(
        "period_start_date", TIMESTAMP
    )
    period_end_date: Mapped[Optional[datetime]] = mapped_column(
        "period_end_date", TIMESTAMP
    )
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"))
    participating_organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id")
    )
    # all other FHIR properties not included yet in our models.
    data: Mapped[Dict[str, Any]] = mapped_column("data", JSON)

    organization: Mapped["Organization"] = relationship(foreign_keys=[organization_id])
    participating_organization: Mapped["Organization"] = relationship(
        foreign_keys=[participating_organization_id]
    )
    endpoint: Mapped[Optional[List["AffiliationEndpoint"]]] = relationship()
    code: Mapped[Optional[List["OrganizationAffiliationRole"]]] = relationship()
    speciality: Mapped[Optional[List["AffiliationPracticeCode"]]] = relationship()
