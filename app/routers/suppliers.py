import logging

from fastapi import APIRouter, Depends
from opentelemetry import trace
from starlette import status
from starlette.responses import Response

from app.authentication import authenticated_ura
from app.container import get_supplying_service
from app.data import UraNumber
from app.models.supplier.dto import UpdateSupplierRequest
from app.models.supplier.model import SupplierModel, UraNumberModel
from app.services.supplier_service import SupplierService

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/supplier",
    tags=["Endpoint suppliers"],
)


@router.post(
    "/get-update-supplier",
    summary="Get the update supplier endpoint",
    response_model=SupplierModel,
    status_code=status.HTTP_200_OK,
)
def get(
    ura_number: UraNumberModel,
    supplying_service: SupplierService = Depends(get_supplying_service),
    _: UraNumber = Depends(authenticated_ura),
) -> SupplierModel:
    """
    Get the supplier's address by URA number. Authentication is done via UZI-server certificates
    """
    span = trace.get_current_span()
    span.update_name(f"POST {router.prefix}/get-update-supplier ura_number={str(ura_number.ura_number)}")
    supplier = supplying_service.get_one(ura_number=ura_number.ura_number)
    span.set_attribute("data.supplier", str(supplier))
    return supplier


@router.post(
    "",
    summary="Register a new update supplier endpoint. Only one update supplier endpoint per care provider is supported",
    response_model=SupplierModel,
    status_code=status.HTTP_201_CREATED,
)
def post(
    supplier: SupplierModel,
    supplying_service: SupplierService = Depends(get_supplying_service),
    _: UraNumber = Depends(authenticated_ura),
) -> SupplierModel:
    """
    Adds an address to a supplier. Authentication is done via UZI-server certificates
    Only **ONE** address per supplier is supported.
    """
    span = trace.get_current_span()
    span.update_name(f"POST {router.prefix} supplier={str(supplier)}")
    supplier = supplying_service.add_one(supplier)
    span.set_attribute("data.supplier", str(supplier))
    return supplier


@router.patch(
    "",
    summary="Update an existing update supplier endpoint",
    response_model=SupplierModel,
    status_code=status.HTTP_200_OK,
)
def patch(
    supplier: UpdateSupplierRequest,
    supplying_service: SupplierService = Depends(get_supplying_service),
    _: UraNumber = Depends(authenticated_ura),
) -> SupplierModel:
    """
    Updates an address of a supplier. Authentication is done via UZI-server certificates
    """
    span = trace.get_current_span()
    span.update_name(f"PATCH {router.prefix} supplier={str(supplier)}")
    updated_supplier = supplying_service.update_one(supplier)
    span.set_attribute("data.supplier", str(updated_supplier))
    return updated_supplier


@router.delete(
    "",
    summary="Delete an existing update supplier endpoint",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    ura_number: UraNumberModel,
    supplying_service: SupplierService = Depends(get_supplying_service),
    _: UraNumber = Depends(authenticated_ura),
) -> Response:
    """
    Deletes a supplier's address. Authentication is done via UZI-server certificates
    """
    span = trace.get_current_span()
    span.update_name(f"DELETE {router.prefix} ura_number={str(ura_number.ura_number)}")
    supplying_service.delete_one(ura_number.ura_number)
    span.set_attribute("data.supplier_deleted", str(True))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
