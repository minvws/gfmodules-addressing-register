from typing import Optional, List, Any
from pydantic import BaseModel, field_serializer, field_validator

from app.data import UraNumber, DataDomain


class AddressURLParameters(BaseModel):
    name: str
    type: str
    required: bool
    description: str
    value: Optional[str] | Optional[List[str]] = None


class Address(BaseModel):
    ura_number: UraNumber
    data_domain: DataDomain
    endpoint: str
    request_type: str
    parameters: List[AddressURLParameters]


    @field_validator('ura_number', mode='before')
    @classmethod
    def validate_ura_number(cls, val: str|UraNumber) -> UraNumber:
        if isinstance(val, UraNumber):
            return val
        return UraNumber(val)

    @field_validator('data_domain', mode='before')
    @classmethod
    def serialize_dd(cls, val: str) -> DataDomain:
        return DataDomain(val)

    @field_serializer('ura_number')
    def serialize_ura_number(self, ura_number: UraNumber) -> str:
        return str(ura_number)

    @field_serializer('data_domain')
    def serialize_dt(self, data_domain: DataDomain, _info: Any) -> str:
        return str(data_domain)
