from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


# ===========================================
# 物料 (Material)
# ===========================================
class MaterialCreate(BaseModel):
    material_code: str = Field(..., min_length=1, max_length=50, description="物料编码")
    name: str = Field(..., min_length=1, max_length=100, description="物料名称")
    unit: str = Field(..., min_length=1, max_length=20, description="计量单位")
    category: Optional[str] = Field(None, max_length=50, description="物料分类")
    safety_stock: int = Field(default=0, ge=0, description="安全库存")
    description: Optional[str] = Field(None, description="描述")


class MaterialUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="物料名称")
    unit: Optional[str] = Field(None, max_length=20, description="计量单位")
    category: Optional[str] = Field(None, max_length=50, description="物料分类")
    safety_stock: Optional[int] = Field(None, ge=0, description="安全库存")
    description: Optional[str] = Field(None, description="描述")


class MaterialResponse(BaseModel):
    id: int
    material_code: str
    name: str
    unit: str
    category: Optional[str]
    safety_stock: int
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===========================================
# 库存 (Inventory)
# ===========================================
class MaterialReceiveRequest(BaseModel):
    material_id: int = Field(..., gt=0, description="物料ID")
    quantity: int = Field(..., gt=0, description="入库数量")
    location_code: str = Field(..., min_length=1, description="库位编码")
    batch_number: Optional[str] = Field(None, description="批次号")


class MaterialDispatchRequest(BaseModel):
    material_id: int = Field(..., gt=0, description="物料ID")
    quantity: int = Field(..., gt=0, description="出库数量")
    location_code: str = Field(..., min_length=1, description="库位编码")
    batch_number: Optional[str] = Field(None, description="批次号")
    reference_type: Optional[str] = Field(None, description="关联单据类型")
    reference_id: Optional[int] = Field(None, description="关联单据ID")


class InventoryResponse(BaseModel):
    id: int
    material_id: Optional[int]
    product_id: Optional[int]
    location_code: str
    batch_number: Optional[str]
    available_qty: int
    locked_qty: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MaterialReceiveResponse(BaseModel):
    inventory_id: int
    available_qty: int
    message: str


class StocktakeRequest(BaseModel):
    inventory_id: int = Field(..., gt=0, description="库存记录ID")
    actual_qty: int = Field(..., ge=0, description="实际盘点数量")
    remark: Optional[str] = Field(None, description="备注")


# ===========================================
# 库存变动日志 (InventoryTransaction)
# ===========================================
class InventoryTransactionResponse(BaseModel):
    id: int
    inventory_id: int
    transaction_type: str
    quantity: int
    reference_type: Optional[str]
    reference_id: Optional[int]
    operator_id: Optional[int]
    remark: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ===========================================
# 库位 (WarehouseLocation)
# ===========================================
class WarehouseLocationCreate(BaseModel):
    warehouse_code: str = Field(..., min_length=1, max_length=20, description="仓库编码")
    zone_code: Optional[str] = Field(None, max_length=20, description="库区编码")
    shelf_code: Optional[str] = Field(None, max_length=20, description="货架编码")
    layer_code: Optional[str] = Field(None, max_length=10, description="层编码")
    position_code: Optional[str] = Field(None, max_length=10, description="位编码")
    capacity: Optional[int] = Field(None, ge=0, description="容量")


class WarehouseLocationResponse(BaseModel):
    id: int
    warehouse_code: str
    zone_code: Optional[str]
    shelf_code: Optional[str]
    layer_code: Optional[str]
    position_code: Optional[str]
    capacity: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
