from typing import Optional, List, Any
from pydantic import BaseModel, field_serializer

from app.data import ProviderID, DataDomain


class AddressURLParameters(BaseModel):
    name: str
    type: str
    required: bool
    description: str
    value: Optional[str] | Optional[List[str]] = None


class Address(BaseModel):
    provider_id: ProviderID
    data_domain: DataDomain
    endpoint: str
    request_type: str
    parameters: List[AddressURLParameters]

    @field_serializer('provider_id')
    def serialize_provider_id(self, provider_id: ProviderID) -> str:
        return str(provider_id)

    @field_serializer('data_domain')
    def serialize_dt(self, data_domain: DataDomain, _info: Any) -> str:
        return str(data_domain)