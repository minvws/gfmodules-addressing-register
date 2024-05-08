from typing import Optional, List
from pydantic import BaseModel


class AddressURLParameters(BaseModel):
    name: str
    type: str
    required: bool
    description: str
    value: Optional[str] | Optional[List[str]] = None


class AddressBase(BaseModel):
    class Config:
        from_attributes = True

    provider_id: str
    data_domain: str


class Address(AddressBase):
    endpoint: str
    request_type: str
    parameters: List[AddressURLParameters]
