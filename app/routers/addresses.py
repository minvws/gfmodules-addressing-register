import logging
from typing import List

from fastapi import APIRouter, Depends
from opentelemetry import trace


from app.container import get_addressing_service
from app.models.address.model import Address
from app.services.addressing_service import AddressingService
from app.models.address.dto import DeleteAddressResponse, AddressRequest

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
    req: AddressRequest,
    addressing_service: AddressingService = Depends(get_addressing_service),
) -> Address:
    """
    Returns an addressing object based on parameters in request body
    """
    span = trace.get_current_span()
    span.update_name(f"POST /metadata_endpoint data_domain={req.data_domain} ura_number={req.ura_number}")

    ret_value = addressing_service.get_provider_address(ura_number=req.ura_number, data_domain=req.data_domain)

    span.set_attribute("data.address", ret_value.endpoint)
    return ret_value


@router.post(
    "/get-many",
    summary="Returns many providers addresses",
    response_model=list[Address],
)
def get_many_addresses(
    req: list[AddressRequest],
    addressing_service: AddressingService = Depends(get_addressing_service),
) -> list[Address]:
    return addressing_service.get_many_providers_addresses(req)


@router.post(
    "/add-one",
    summary="adds a single Provider Address to database",
    response_model=Address,
)
def add_one_address(
    req: Address,
    addressing_service: AddressingService = Depends(get_addressing_service),
) -> Address:
    span = trace.get_current_span()
    span.set_attribute("data.ura_number", str(req.ura_number))
    span.set_attribute("data.data_domain", str(req.data_domain))
    span.set_attribute("data.endpoint", req.endpoint)
    span.set_attribute("data.request_type", req.request_type)

    addressing_service.add_provider_address(req)
    return req


@router.post(
    "/add-many",
    summary="adds an many of Providers Addresses to the Database",
    response_model=list[Address],
)
def add_many_addresses(
    req: list[Address],
    addressing_service: AddressingService = Depends(get_addressing_service),
) -> List[Address]:
    addressing_service.add_many_addresses(req)
    return req


@router.delete(
    "/delete-one", summary="delete one provider address", response_model=DeleteAddressResponse
)
def delete_one_address(
    req: AddressRequest,
    addressing_service: AddressingService = Depends(get_addressing_service),
) -> DeleteAddressResponse:
    span = trace.get_current_span()
    span.set_attribute("data.ura_number", str(req.ura_number))
    span.set_attribute("data.data_domain", str(req.data_domain))

    result = addressing_service.remove_one_address(ura_number=req.ura_number, data_domain=req.data_domain)
    return DeleteAddressResponse(
        meta=result.meta,
        addresses=result.addresses,
    )


@router.delete(
    "/delete-many",
    summary="delete many providers addresses",
    response_model=DeleteAddressResponse,
)
def delete_many_addresses(
    req: List[AddressRequest],
    addressing_service: AddressingService = Depends(get_addressing_service),
) -> DeleteAddressResponse:

    result = addressing_service.remove_many_addresses(req)
    return DeleteAddressResponse(
        meta=result.meta,
        addresses=result.addresses,
    )
