from typing import List, Optional, Any

from pydantic import BaseModel, field_serializer

from app.data import ProviderID, DataDomain
from app.models.address.model import Address


class Meta(BaseModel):
    total: int
    deleted: int
    limit: Optional[int] = None
    offset: Optional[int] = None


class DeleteAddressResult(BaseModel):
    meta: Meta
    addresses: List[Address]


class DeleteAddressResponse(BaseModel):
    meta: Meta
    addresses: List[Address]


class AddressRequest(BaseModel):
    provider_id: ProviderID
    data_domain: DataDomain

    @field_serializer('provider_id')
    def serialize_provider_id(self, provider_id: ProviderID, _info: Any) -> str:
        return str(provider_id)

    @field_serializer('data_domain')
    def serialize_dd(self, data_domain: DataDomain, _info: Any) -> str:
        return str(data_domain)