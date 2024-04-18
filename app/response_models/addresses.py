from typing import Optional, List
from pydantic import BaseModel


class AddressesRequest(BaseModel):
    provider_id: str
    data_domain: str


class AddressURLParameters(BaseModel):
    name: str
    type: str
    required: bool
    description: str
    value: Optional[str] = None


class AddressesResponse(BaseModel):
    endpoint: str
    request_type: str
    parameters: List[AddressURLParameters] = []

    class Config:
        orm_mode = True
