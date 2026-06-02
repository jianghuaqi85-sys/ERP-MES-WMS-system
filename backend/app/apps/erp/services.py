import uuid
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.constants import BOMStatus, PurchaseOrderStatus, SalesOrderStatus, WorkOrderStatus
from app.apps.erp.models import (
    BOM, BOMItem, Product, PurchaseOrder, PurchaseOrderItem, SalesOrder, Supplier,
)
from app.apps.erp.schemas import (
    BOMCreate, ProductCreate, ProductUpdate, PurchaseOrderCreate,
    SalesOrderCreate, SalesOrderUpdate, SupplierCreate, SupplierUpdate,
)
from app.apps.mes.models import WorkOrder


class ERPService:
    # ===========================================
    # 产品管理
    # ===========================================
    @staticmethod
    def create_product(db: Session, request: ProductCreate) -> Product:
        existing = db.query(Product).filter(Product.product_code == request.product_code).first()
        if existing:
            raise ValueError(f"产品编码 {request.product_code} 已存在")
        product = Product(**request.model_dump())
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def update_product(db: Session, product_id: int, request: ProductUpdate) -> Product:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"产品ID {product_id} 不存在")
        for key, value in request.model_dump(exclude_unset=True).items():
            setattr(product, key, value)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: int) -> None:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"产品ID {product_id} 不存在")
        db.delete(product)
        db.commit()

    # ===========================================
    # BOM 管理
    # ===========================================
    @staticmethod
    def create_bom(db: Session, request: BOMCreate) -> BOM:
        # 验证产品存在
        product = db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            raise ValueError(f"产品ID {request.product_id} 不存在")

        bom = BOM(
            product_id=request.product_id,
            version=request.version,
            remark=request.remark,
            status=BOMStatus.DRAFT,
        )
        db.add(bom)
        db.flush()

        for item in request.items:
            bom_item = BOMItem(
                bom_id=bom.id,
                material_id=item.material_id,
                quantity=item.quantity,
                unit=item.unit,
                remark=item.remark,
            )
            db.add(bom_item)

        db.commit()
        db.refresh(bom)
        return bom

    @staticmethod
    def activate_bom(db: Session, bom_id: int) -> BOM:
        bom = db.query(BOM).filter(BOM.id == bom_id).first()
        if not bom:
            raise ValueError(f"BOM ID {bom_id} 不存在")

        # 将同产品的其他 ACTIVE BOM 设为 OBSOLETE
        db.query(BOM).filter(
            BOM.product_id == bom.product_id,
            BOM.status == BOMStatus.ACTIVE,
            BOM.id != bom_id,
        ).update({"status": BOMStatus.OBSOLETE})

        bom.status = BOMStatus.ACTIVE
        bom.is_default = True
        db.commit()
        db.refresh(bom)
        return bom

    # ===========================================
    # 销售订单管理
    # ===========================================
    @staticmethod
    def create_sales_order(db: Session, request: SalesOrderCreate) -> SalesOrder:
        # 验证产品存在
        product = db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            raise ValueError(f"产品ID {request.product_id} 不存在")

        order_number = f"SO-{uuid.uuid4().hex[:8].upper()}"
        total_amount = (request.unit_price or Decimal(0)) * request.quantity

        order = SalesOrder(
            order_number=order_number,
            customer_name=request.customer_name,
            customer_contact=request.customer_contact,
            product_id=request.product_id,
            quantity=request.quantity,
            unit_price=request.unit_price,
            total_amount=total_amount,
            status=SalesOrderStatus.DRAFT,
            remark=request.remark,
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def update_sales_order(db: Session, order_id: int, request: SalesOrderUpdate) -> SalesOrder:
        order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not order:
            raise ValueError(f"销售订单ID {order_id} 不存在")
        if order.status not in [SalesOrderStatus.DRAFT, SalesOrderStatus.PENDING]:
            raise ValueError("只能修改草稿或待确认状态的订单")

        for key, value in request.model_dump(exclude_unset=True).items():
            setattr(order, key, value)

        # 重新计算总金额
        if order.unit_price:
            order.total_amount = order.unit_price * order.quantity

        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def confirm_sales_order(db: Session, order_id: int) -> SalesOrder:
        """确认销售订单 → 自动创建生产工单"""
        order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not order:
            raise ValueError(f"销售订单ID {order_id} 不存在")
        if order.status != SalesOrderStatus.DRAFT:
            raise ValueError("只能确认草稿状态的订单")

        # 查找默认 BOM
        default_bom = db.query(BOM).filter(
            BOM.product_id == order.product_id,
            BOM.status == BOMStatus.ACTIVE,
        ).first()

        # 创建生产工单
        wo_number = f"WO-{uuid.uuid4().hex[:8].upper()}"
        work_order = WorkOrder(
            work_order_number=wo_number,
            sales_order_id=order.id,
            bom_id=default_bom.id if default_bom else None,
            product_id=order.product_id,
            planned_quantity=order.quantity,
            status=WorkOrderStatus.PLANNED,
        )
        db.add(work_order)

        order.status = SalesOrderStatus.CONFIRMED
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def ship_sales_order(db: Session, order_id: int) -> SalesOrder:
        """发货 → 扣减成品库存"""
        from app.apps.wms.models import Inventory
        from app.core.constants import InventoryLocation

        order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not order:
            raise ValueError(f"销售订单ID {order_id} 不存在")
        if order.status != SalesOrderStatus.READY_TO_SHIP:
            raise ValueError("只能发货待发货状态的订单")

        # 扣减成品库存
        inventory = (
            db.query(Inventory)
            .filter(
                Inventory.product_id == order.product_id,
                Inventory.location_code == InventoryLocation.FINISHED_GOODS,
            )
            .with_for_update()
            .first()
        )
        if not inventory or inventory.available_qty < order.quantity:
            raise ValueError("成品库存不足，无法发货")

        inventory.available_qty -= order.quantity
        order.status = SalesOrderStatus.SHIPPED

        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def cancel_sales_order(db: Session, order_id: int) -> SalesOrder:
        order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
        if not order:
            raise ValueError(f"销售订单ID {order_id} 不存在")
        if order.status == SalesOrderStatus.SHIPPED:
            raise ValueError("已发货的订单不能取消")

        order.status = SalesOrderStatus.CANCELLED
        db.commit()
        db.refresh(order)
        return order

    # ===========================================
    # 供应商管理
    # ===========================================
    @staticmethod
    def create_supplier(db: Session, request: SupplierCreate) -> Supplier:
        existing = db.query(Supplier).filter(Supplier.code == request.code).first()
        if existing:
            raise ValueError(f"供应商编码 {request.code} 已存在")
        supplier = Supplier(**request.model_dump())
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
        return supplier

    @staticmethod
    def update_supplier(db: Session, supplier_id: int, request: SupplierUpdate) -> Supplier:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            raise ValueError(f"供应商ID {supplier_id} 不存在")
        for key, value in request.model_dump(exclude_unset=True).items():
            setattr(supplier, key, value)
        db.commit()
        db.refresh(supplier)
        return supplier

    @staticmethod
    def delete_supplier(db: Session, supplier_id: int) -> None:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            raise ValueError(f"供应商ID {supplier_id} 不存在")
        db.delete(supplier)
        db.commit()

    # ===========================================
    # 采购订单管理
    # ===========================================
    @staticmethod
    def create_purchase_order(db: Session, request: PurchaseOrderCreate) -> PurchaseOrder:
        supplier = db.query(Supplier).filter(Supplier.id == request.supplier_id).first()
        if not supplier:
            raise ValueError(f"供应商ID {request.supplier_id} 不存在")

        po_number = f"PO-{uuid.uuid4().hex[:8].upper()}"
        po = PurchaseOrder(
            po_number=po_number,
            supplier_id=request.supplier_id,
            status=PurchaseOrderStatus.DRAFT,
            remark=request.remark,
        )
        db.add(po)
        db.flush()

        total_amount = Decimal(0)
        for item in request.items:
            po_item = PurchaseOrderItem(
                purchase_order_id=po.id,
                material_id=item.material_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            db.add(po_item)
            if item.unit_price:
                total_amount += item.unit_price * item.quantity

        po.total_amount = total_amount
        db.commit()
        db.refresh(po)
        return po

    # ===========================================
    # 工单创建（ERP 下发）
    # ===========================================
    @staticmethod
    def create_work_order(db: Session, request) -> WorkOrder:
        product = db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            raise ValueError(f"成品ID {request.product_id} 不存在")

        wo_number = f"WO-{uuid.uuid4().hex[:8].upper()}"
        work_order = WorkOrder(
            work_order_number=wo_number,
            product_id=request.product_id,
            planned_quantity=request.planned_quantity,
            sales_order_id=request.sales_order_id,
            bom_id=request.bom_id,
            status=WorkOrderStatus.PLANNED,
            remark=request.remark,
        )
        db.add(work_order)
        db.commit()
        db.refresh(work_order)
        return work_order
