from typing import Optional

from app.models.supplier.model import UraNumberModel

class UpdateSupplierRequest(UraNumberModel):
    care_provider_name: Optional[str] = None
    update_supplier_endpoint: Optional[str] = None
