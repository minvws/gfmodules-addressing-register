from pydantic import BaseModel, field_serializer, field_validator

from app.data import UraNumber


class UraNumberModel(BaseModel):
    ura_number: UraNumber

    @field_validator("ura_number", mode="before")
    @classmethod
    def validate_ura_number(cls, val: str | UraNumber) -> UraNumber:
        if isinstance(val, UraNumber):
            return val
        return UraNumber(val)

    @field_serializer("ura_number")
    def serialize_ura_number(self, ura_number: UraNumber) -> str:
        return str(ura_number)


class SupplierModel(UraNumberModel):
    care_provider_name: str
    update_supplier_endpoint: str
