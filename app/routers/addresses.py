import logging
from typing import List

from fastapi import APIRouter, Depends
from opentelemetry import trace


from app.container import get_addressing_service
from app.models.address.model import Address
from app.services.addressing_service import AddressingService
from app.models.address.dto import (
    AddressRequest,
    DeleteAddress,
)

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/metadata_endpoint",
    tags=["Addresses"],
)


@router.post(
    "",
    summary="Returns an address metadata for a single provider",
    response_model=Address,
)
def get_address(
    data: AddressRequest,
    addressing_service: AddressingService = Depends(get_addressing_service),
) -> Address:
    """
    Returns an addressing object based on parameters in request body
    """
    span = trace.get_current_span()
    span.set_attribute("data.data_domain", data.data_domain)
    span.set_attribute("data.provider_id", data.provider_id)
    return addressing_service.get_provider_address(
        provider_id=data.provider_id, data_domain=data.data_domain
    )


@router.post(
    "/get-many",
    summary="Returns many providers addresses",
    response_model=Address,
)
def get_many_addresses(
    data: List[AddressRequest],
    addressing_service: AddressingService = Depends(get_addressing_service),
) -> List[Address]:
    return addressing_service.get_many_providers_addresses(data)


@router.post(
    "/add-one",
    summary="adds a single Provider Address to database",
    response_model=Address,
)
def add_one_address(
    data: Address,
    addressing_service: AddressingService = Depends(get_addressing_service),
) -> Address:
    span = trace.get_current_span()
    span.set_attribute("data.provider_id", data.provider_id)
    span.set_attribute("data.data_domain", data.data_domain)
    span.set_attribute("data.endpoint", data.endpoint)
    span.set_attribute("data.request_type", data.request_type)

    return addressing_service.add_provider_address(data)


@router.post(
    "/add-many",
    summary="adds an many of Providers Addresses to the Database",
    response_model=List[Address],
)
def add_many_addresses(
    data: List[Address],
    addressing_service: AddressingService = Depends(get_addressing_service),
) -> List[Address]:
    return addressing_service.add_many_addresses(data)


@router.delete(
    "/delete-one", summary="delete one provider address", response_model=DeleteAddress
)
def delete_one_address(
    data: AddressRequest,
    addressing_service: AddressingService = Depends(get_addressing_service),
) -> DeleteAddress:
    span = trace.get_current_span()
    span.set_attribute("data.provider_id", data.provider_id)
    span.set_attribute("data.data_domain", data.data_domain)
    return addressing_service.remove_one_address(data.provider_id, data.data_domain)


@router.delete(
    "/delete-many",
    summary="delete many providers addresses",
    response_model=DeleteAddress,
)
def delete_many_addresses(
    data: List[AddressRequest],
    addressing_service: AddressingService = Depends(get_addressing_service),
) -> DeleteAddress:
    return addressing_service.remove_many_addresses(data)
