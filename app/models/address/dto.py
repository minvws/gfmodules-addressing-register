from typing import List, Optional

from pydantic import BaseModel, field_validator

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

    @field_validator('ura_number', mode='before')
    @classmethod
    def serialize_ura_number(cls, val: str) -> UraNumber:
        if isinstance(val, UraNumber):
            # Something in the unittests will try to serialize an already existing uranumber to uranumber.
            # so we need to make sure we don't convert it twice.
            return val

        return UraNumber(val)

    @field_validator('data_domain', mode='before')
    @classmethod
    def serialize_dd(cls, val: str) -> DataDomain:
        return DataDomain(val)
