from sqlalchemy import select
from app.db.decorator import repository
from app.db.entities.endpoint.endpoint_payload import EndpointPayload
from app.db.entities.value_sets.endpoint_payload_types import EndpointPayloadType
from app.db.repositories.repository_base import RepositoryBase
from app.db.repositories.repository_exception import RepositoryException


@repository(EndpointPayload)
class EndpointPayloadTypeRepository(RepositoryBase):
    def get(self, code: str) -> EndpointPayloadType:
        stmt = select(EndpointPayloadType).filter_by(code=code)
        payload_type = self.db_session.session.execute(stmt).scalars().first()
        if payload_type is not None:
            return payload_type
        raise RepositoryException("Failed to retrieve endpoint payload type with code %s", code)
