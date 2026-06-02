from sqlalchemy.orm import Session

from app.apps.wms.models import Inventory, InventoryTransaction, Material
from app.apps.wms.schemas import MaterialDispatchRequest, MaterialReceiveRequest, StocktakeRequest
from app.core.constants import InventoryTransactionType


class WMSService:
    @staticmethod
    def receive_material(
        db: Session, request: MaterialReceiveRequest, operator_id: int = None
    ) -> Inventory:
        """入库操作"""
        # 1. 检查物料是否存在
        material = db.query(Material).filter(Material.id == request.material_id).first()
        if not material:
            raise ValueError(f"物料ID {request.material_id} 不存在")

        # 2. 查找或创建库存记录（加行级锁防并发丢失更新）
        inventory = (
            db.query(Inventory)
            .filter(
                Inventory.material_id == request.material_id,
                Inventory.location_code == request.location_code,
            )
            .with_for_update()
            .first()
        )

        if inventory:
            inventory.available_qty += request.quantity
        else:
            inventory = Inventory(
                material_id=request.material_id,
                location_code=request.location_code,
                batch_number=request.batch_number,
                available_qty=request.quantity,
                locked_qty=0,
            )
            db.add(inventory)

        db.flush()

        # 3. 记录库存变动日志
        transaction = InventoryTransaction(
            inventory_id=inventory.id,
            transaction_type=InventoryTransactionType.INBOUND,
            quantity=request.quantity,
            reference_type="MATERIAL_RECEIVE",
            operator_id=operator_id,
            remark=f"物料入库: {material.name} x {request.quantity}",
        )
        db.add(transaction)

        db.commit()
        db.refresh(inventory)
        return inventory

    @staticmethod
    def dispatch_material(
        db: Session, request: MaterialDispatchRequest, operator_id: int = None
    ) -> Inventory:
        """出库操作"""
        material = db.query(Material).filter(Material.id == request.material_id).first()
        if not material:
            raise ValueError(f"物料ID {request.material_id} 不存在")

        inventory = (
            db.query(Inventory)
            .filter(
                Inventory.material_id == request.material_id,
                Inventory.location_code == request.location_code,
            )
            .with_for_update()
            .first()
        )

        if not inventory or inventory.available_qty < request.quantity:
            raise ValueError(
                f"物料ID {request.material_id} 在库位 {request.location_code} 的库存不足"
            )

        inventory.available_qty -= request.quantity
        db.flush()

        # 记录库存变动日志
        transaction = InventoryTransaction(
            inventory_id=inventory.id,
            transaction_type=InventoryTransactionType.OUTBOUND,
            quantity=-request.quantity,
            reference_type=request.reference_type,
            reference_id=request.reference_id,
            operator_id=operator_id,
            remark=f"物料出库: {material.name} x {request.quantity}",
        )
        db.add(transaction)

        db.commit()
        db.refresh(inventory)
        return inventory

    @staticmethod
    def stocktake(
        db: Session, request: StocktakeRequest, operator_id: int = None
    ) -> Inventory:
        """库存盘点"""
        inventory = (
            db.query(Inventory)
            .filter(Inventory.id == request.inventory_id)
            .with_for_update()
            .first()
        )
        if not inventory:
            raise ValueError(f"库存记录ID {request.inventory_id} 不存在")

        diff = request.actual_qty - inventory.available_qty
        inventory.available_qty = request.actual_qty
        db.flush()

        # 记录盘点变动日志
        transaction = InventoryTransaction(
            inventory_id=inventory.id,
            transaction_type=InventoryTransactionType.ADJUSTMENT,
            quantity=diff,
            reference_type="STOCKTAKE",
            operator_id=operator_id,
            remark=f"库存盘点调整: {request.remark or ''}",
        )
        db.add(transaction)

        db.commit()
        db.refresh(inventory)
        return inventory
