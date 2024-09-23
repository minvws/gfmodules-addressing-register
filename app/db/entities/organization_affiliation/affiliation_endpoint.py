from uuid import UUID
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.entities.mixin.common_mixin import CommonMixin
from app.db.entities.base import Base
from app.db.entities.endpoint.endpoint import Endpoint


class AffiliationEndpoint(CommonMixin, Base):
    __tablename__ = "organization_affiliation_endpoints"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    affiliation_id: Mapped[UUID] = mapped_column(
        ForeignKey("organization_affiliations.id")
    )
    endpoint_id: Mapped[UUID] = mapped_column(ForeignKey("endpoints.id"))

    endpoint: Mapped["Endpoint"] = relationship()
