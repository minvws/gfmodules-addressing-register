from typing import Optional, List, Any
from pydantic import BaseModel, field_serializer

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

    @field_serializer('ura_number')
    def serialize_ura_number(self, ura_number: UraNumber) -> str:
        return str(ura_number)

    @field_serializer('data_domain')
    def serialize_dt(self, data_domain: DataDomain, _info: Any) -> str:
        return str(data_domain)
