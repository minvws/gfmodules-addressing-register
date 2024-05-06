import logging

from fastapi import APIRouter, Depends, HTTPException
from opentelemetry import trace

from app.db.models.address import Address
from app.container import get_addressing_service
from app.services.addressing_service import AddressingService
from app.response_models.addresses import AddressesRequest

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/metadata_endpoint",
    summary="Search for examples based on the query parameter",
    tags=["Addresses"],
    response_model=None,
)
def get_address(
    data: AddressesRequest,
    addressing_service: AddressingService = Depends(get_addressing_service),
) -> Address:
    """
    Returns an addressing object based on parameters in request body
    """

    span = trace.get_current_span()
    span.set_attribute("data.data_domain", data.data_domain)
    span.set_attribute("data.provider_id", data.provider_id)

    address = addressing_service.get_provider_addressing(
        provider_id=data.provider_id, data_domain=data.data_domain
    )
    if address is None:
        raise HTTPException(status_code=404, detail="Requested addressing not found")

    return address
