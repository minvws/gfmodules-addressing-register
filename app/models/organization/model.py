import uuid
from typing import Optional
from pydantic import BaseModel, field_validator, field_serializer

from app.data import UraNumber


class OrganizationModel(BaseModel):
    ura_number: UraNumber
    active: bool
    name: str
    description: Optional[str] = None
    parent_organization_id: Optional[uuid.UUID] = None

    @field_validator('ura_number', mode='before')
    @classmethod
    def validate_ura_number(cls, val: str | UraNumber) -> UraNumber:
        if isinstance(val, UraNumber):
            return val
        return UraNumber(val)

    @field_serializer('ura_number')
    def serialize_ura_number(self, ura_number: UraNumber) -> str:
        return str(ura_number)
