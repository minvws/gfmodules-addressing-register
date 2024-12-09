import logging

from app.data import UraNumber
from app.db.db import Database
from app.db.entities.supplier_endpoint import SupplierEndpoint
from app.db.repositories.suppliers_repository import SuppliersRepository
from app.exceptions.service_exceptions import (
    ResourceNotAddedException,
    ResourceNotFoundException,
)
from app.models.supplier.dto import UpdateSupplierRequest
from app.models.supplier.model import SupplierModel

logger = logging.getLogger(__name__)


class SupplierService:
    def __init__(self, database: Database):
        self.database = database

    def get_one(self, ura_number: UraNumber) -> SupplierModel:
        with self.database.get_db_session() as session:
            supply_repository = session.get_repository(SuppliersRepository)
            result = supply_repository.get(ura_number=str(ura_number))
            if result is None:
                raise ResourceNotFoundException()
            return self.hydrate_supplier(result)

    def add_one(self, supplier: SupplierModel) -> SupplierModel:
        with self.database.get_db_session() as session:
            supply_repository = session.get_repository(SuppliersRepository)
            if supply_repository.get(str(supplier.ura_number)) is not None:
                raise ResourceNotAddedException(
                    detail="Care provider already has an update supplier endpoint set up, cannot have more than one"
                )
            new_supplier = SupplierEndpoint(
                ura_number=str(supplier.ura_number),
                care_provider_name=supplier.care_provider_name,
                update_supplier_endpoint=supplier.update_supplier_endpoint,
            )
            result = supply_repository.create(new_supplier)
            return self.hydrate_supplier(result)

    def update_one(self, supplier: UpdateSupplierRequest) -> SupplierModel:
        with self.database.get_db_session() as session:
            supply_repository = session.get_repository(SuppliersRepository)
            db_supplier = supply_repository.get(ura_number=str(supplier.ura_number))
            if db_supplier is None:
                raise ResourceNotFoundException()
            if supplier.update_supplier_endpoint is not None:
                db_supplier.update_supplier_endpoint = supplier.update_supplier_endpoint
            if supplier.care_provider_name is not None:
                db_supplier.care_provider_name = supplier.care_provider_name
            result = supply_repository.update(db_supplier)
            return self.hydrate_supplier(result)

    def delete_one(self, ura_number: UraNumber) -> None:
        with self.database.get_db_session() as session:
            supply_repository = session.get_repository(SuppliersRepository)
            entity = supply_repository.get(ura_number=str(ura_number))
            if entity is None:
                raise ResourceNotFoundException()
            supply_repository.delete(entity)

    @staticmethod
    def hydrate_supplier(entity: SupplierEndpoint) -> SupplierModel:
        return SupplierModel(
            ura_number=UraNumber(entity.ura_number),
            care_provider_name=entity.care_provider_name,
            update_supplier_endpoint=entity.update_supplier_endpoint,
        )
