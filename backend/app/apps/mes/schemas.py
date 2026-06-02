from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ===========================================
# 工序 (WorkOrderProcess)
# ===========================================
class WorkOrderProcessCreate(BaseModel):
    process_name: str = Field(..., min_length=1, max_length=50, description="工序名称")
    sequence: int = Field(..., gt=0, description="工序顺序")
    planned_start: Optional[datetime] = Field(None, description="计划开始时间")
    planned_end: Optional[datetime] = Field(None, description="计划结束时间")
    remark: Optional[str] = Field(None, description="备注")


class WorkOrderProcessResponse(BaseModel):
    id: int
    work_order_id: int
    process_name: str
    sequence: int
    status: str
    planned_start: Optional[datetime]
    planned_end: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===========================================
# 工单 (WorkOrder)
# ===========================================
class WorkOrderResponse(BaseModel):
    id: int
    work_order_number: str
    sales_order_id: Optional[int]
    bom_id: Optional[int]
    product_id: int
    planned_quantity: int
    actual_quantity: int
    qualified_quantity: int
    defective_quantity: int
    status: str
    planned_start: Optional[datetime]
    planned_end: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    remark: Optional[str]
    processes: List[WorkOrderProcessResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===========================================
# 生产报工
# ===========================================
class ConsumedMaterial(BaseModel):
    material_id: int = Field(..., gt=0, description="物料ID")
    quantity: int = Field(..., gt=0, description="消耗数量")
    inventory_location_code: str = Field(..., min_length=1, description="库位编码")
    material_barcode: str = Field(..., min_length=1, description="物料条码")


class WorkOrderReportRequest(BaseModel):
    produced_quantity: int = Field(..., gt=0, description="产出数量")
    qualified_quantity: Optional[int] = Field(None, ge=0, description="合格数量")
    defective_quantity: Optional[int] = Field(None, ge=0, description="不良数量")
    product_barcode: str = Field(..., min_length=1, description="成品条码")
    consumed_materials: List[ConsumedMaterial] = Field(..., min_length=1, description="消耗物料列表")


class WorkOrderReportResponse(BaseModel):
    message: str
    traceability_record_ids: List[int]
