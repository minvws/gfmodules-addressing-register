from typing import List

from pydantic import BaseModel

from app.models.address.model import AddressBase, Address
from app.models.meta.model import Meta


class AddressResponseBase(BaseModel):
    meta: Meta


class AddressRequest(AddressBase):
    pass


class AddressResponse(Address):
    pass


class CreateAddress(Address):
    pass


class DeleteAddress(AddressResponseBase):
    data: Address | List[Address] | List[CreateAddress]
