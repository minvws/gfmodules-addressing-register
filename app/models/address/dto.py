from typing import List, Optional, Any

from pydantic import BaseModel, field_serializer

from app.data import UraNumber, DataDomain
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
    ura_number: UraNumber
    data_domain: DataDomain

    @field_serializer('ura_number')
    def serialize_ura_number(self, ura_number: UraNumber, _info: Any) -> str:
        return str(ura_number)

    @field_serializer('data_domain')
    def serialize_dd(self, data_domain: DataDomain, _info: Any) -> str:
        return str(data_domain)
