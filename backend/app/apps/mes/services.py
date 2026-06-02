from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.core.constants import (
    InventoryLocation,
    TraceActionType,
    TraceSourceType,
    TraceTargetType,
    WorkOrderStatus,
)
from app.apps.mes.models import WorkOrder
from app.apps.mes.schemas import WorkOrderReportRequest
from app.apps.traceability.models import TraceabilityRecord
from app.apps.wms.models import Inventory


class MESService:
    @staticmethod
    def start_work_order(db: Session, work_order_id: int) -> WorkOrder:
        """开始生产"""
        work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not work_order:
            raise ValueError(f"工单ID {work_order_id} 不存在")
        if work_order.status not in [WorkOrderStatus.PLANNED, WorkOrderStatus.NOT_STARTED]:
            raise ValueError(f"当前状态 {work_order.status} 无法开始生产")

        work_order.status = WorkOrderStatus.IN_PROGRESS
        work_order.actual_start = datetime.now()
        db.commit()
        db.refresh(work_order)
        return work_order

    @staticmethod
    def complete_work_order(db: Session, work_order_id: int) -> WorkOrder:
        """完成工单"""
        work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not work_order:
            raise ValueError(f"工单ID {work_order_id} 不存在")
        if work_order.status != WorkOrderStatus.IN_PROGRESS:
            raise ValueError("只能完成进行中的工单")

        work_order.status = WorkOrderStatus.COMPLETED
        work_order.actual_end = datetime.now()
        db.commit()
        db.refresh(work_order)
        return work_order

    @staticmethod
    def close_work_order(db: Session, work_order_id: int) -> WorkOrder:
        """关闭工单"""
        work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not work_order:
            raise ValueError(f"工单ID {work_order_id} 不存在")
        if work_order.status != WorkOrderStatus.COMPLETED:
            raise ValueError("只能关闭已完成的工单")

        work_order.status = WorkOrderStatus.CLOSED
        db.commit()
        db.refresh(work_order)
        return work_order

    @staticmethod
    def report_production(
        db: Session, work_order_id: int, request: WorkOrderReportRequest
    ) -> List[int]:
        """
        生产报工核心逻辑。
        事务由调用方 (router) 管理 —— 正常退出时自动 commit，异常时自动 rollback。
        """
        trace_ids: list[int] = []

        # 1. 查找并验证工单（行级锁防并发）
        work_order = (
            db.query(WorkOrder)
            .filter(WorkOrder.id == work_order_id)
            .with_for_update()
            .first()
        )
        if not work_order:
            raise ValueError(f"工单ID {work_order_id} 不存在")

        if work_order.status in [WorkOrderStatus.COMPLETED, WorkOrderStatus.CLOSED]:
            raise ValueError("工单已完成或关闭，无法继续报工")

        # 自动开始工单
        if work_order.status in [WorkOrderStatus.PLANNED, WorkOrderStatus.NOT_STARTED]:
            work_order.status = WorkOrderStatus.IN_PROGRESS
            work_order.actual_start = datetime.now()

        # 2. 扣减原材料库存 (WMS联动)
        for mat in request.consumed_materials:
            inventory = (
                db.query(Inventory)
                .filter(
                    Inventory.material_id == mat.material_id,
                    Inventory.location_code == mat.inventory_location_code,
                )
                .with_for_update()
                .first()
            )

            if not inventory or inventory.available_qty < mat.quantity:
                raise ValueError(
                    f"物料ID {mat.material_id} 在库位 {mat.inventory_location_code} 的库存不足"
                )

            inventory.available_qty -= mat.quantity

            # 3. 写入溯源记录 (Traceability联动)
            trace_record = TraceabilityRecord(
                source_type=TraceSourceType.MATERIAL,
                source_id=mat.material_id,
                source_barcode=mat.material_barcode,
                target_type=TraceTargetType.PRODUCT,
                target_id=work_order.product_id,
                target_barcode=request.product_barcode,
                work_order_id=work_order.id,
                action_type=TraceActionType.ASSEMBLE,
            )
            db.add(trace_record)
            db.flush()  # 获取生成的 trace_record.id
            trace_ids.append(trace_record.id)

        # 4. 增加成品库存 (WMS联动)
        product_inventory = (
            db.query(Inventory)
            .filter(
                Inventory.product_id == work_order.product_id,
                Inventory.location_code == InventoryLocation.FINISHED_GOODS,
            )
            .with_for_update()
            .first()
        )

        if product_inventory:
            product_inventory.available_qty += request.produced_quantity
        else:
            product_inventory = Inventory(
                product_id=work_order.product_id,
                location_code=InventoryLocation.FINISHED_GOODS,
                available_qty=request.produced_quantity,
            )
            db.add(product_inventory)

        # 5. 更新工单状态
        work_order.actual_quantity += request.produced_quantity
        if request.qualified_quantity is not None:
            work_order.qualified_quantity += request.qualified_quantity
        if request.defective_quantity is not None:
            work_order.defective_quantity += request.defective_quantity

        # 判断是否完成
        if work_order.actual_quantity >= work_order.planned_quantity:
            work_order.status = WorkOrderStatus.COMPLETED
            work_order.actual_end = datetime.now()

        db.commit()
        return trace_ids
