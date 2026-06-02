from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


# ===========================================
# 产品 (Product)
# ===========================================
class ProductCreate(BaseModel):
    product_code: str = Field(..., min_length=1, max_length=50, description="成品编码")
    name: str = Field(..., min_length=1, max_length=100, description="成品名称")
    price: Decimal = Field(default=0, ge=0, description="销售价格")
    unit: str = Field(default="pcs", description="计量单位")
    description: Optional[str] = Field(None, description="产品描述")


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="成品名称")
    price: Optional[Decimal] = Field(None, ge=0, description="销售价格")
    unit: Optional[str] = Field(None, description="计量单位")
    description: Optional[str] = Field(None, description="产品描述")


class ProductResponse(BaseModel):
    id: int
    product_code: str
    name: str
    price: Decimal
    unit: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===========================================
# BOM (物料清单)
# ===========================================
class BOMItemCreate(BaseModel):
    material_id: int = Field(..., gt=0, description="物料ID")
    quantity: Decimal = Field(..., gt=0, description="单位用量")
    unit: Optional[str] = Field(None, description="单位")
    remark: Optional[str] = Field(None, description="备注")


class BOMCreate(BaseModel):
    product_id: int = Field(..., gt=0, description="成品ID")
    version: str = Field(default="1.0", description="BOM 版本")
    remark: Optional[str] = Field(None, description="备注")
    items: List[BOMItemCreate] = Field(..., min_length=1, description="BOM 子件列表")


class BOMItemResponse(BaseModel):
    id: int
    material_id: int
    quantity: Decimal
    unit: Optional[str]
    remark: Optional[str]

    class Config:
        from_attributes = True


class BOMResponse(BaseModel):
    id: int
    product_id: int
    version: str
    is_default: bool
    status: str
    remark: Optional[str]
    items: List[BOMItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===========================================
# 销售订单 (SalesOrder)
# ===========================================
class SalesOrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100, description="客户名称")
    customer_contact: Optional[str] = Field(None, max_length=100, description="客户联系方式")
    product_id: int = Field(..., gt=0, description="成品ID")
    quantity: int = Field(..., gt=0, description="销售数量")
    unit_price: Optional[Decimal] = Field(None, ge=0, description="单价")
    remark: Optional[str] = Field(None, description="备注")


class SalesOrderUpdate(BaseModel):
    customer_name: Optional[str] = Field(None, max_length=100, description="客户名称")
    customer_contact: Optional[str] = Field(None, max_length=100, description="客户联系方式")
    quantity: Optional[int] = Field(None, gt=0, description="销售数量")
    unit_price: Optional[Decimal] = Field(None, ge=0, description="单价")
    remark: Optional[str] = Field(None, description="备注")


class SalesOrderResponse(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_contact: Optional[str]
    product_id: int
    quantity: int
    unit_price: Optional[Decimal]
    total_amount: Optional[Decimal]
    status: str
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===========================================
# 供应商 (Supplier)
# ===========================================
class SupplierCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, description="供应商编码")
    name: str = Field(..., min_length=1, max_length=100, description="供应商名称")
    contact_person: Optional[str] = Field(None, max_length=50, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    address: Optional[str] = Field(None, description="地址")


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="供应商名称")
    contact_person: Optional[str] = Field(None, max_length=50, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    address: Optional[str] = Field(None, description="地址")
    status: Optional[str] = Field(None, description="状态")


class SupplierResponse(BaseModel):
    id: int
    code: str
    name: str
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===========================================
# 采购订单 (PurchaseOrder)
# ===========================================
class PurchaseOrderItemCreate(BaseModel):
    material_id: int = Field(..., gt=0, description="物料ID")
    quantity: Decimal = Field(..., gt=0, description="采购数量")
    unit_price: Optional[Decimal] = Field(None, ge=0, description="单价")


class PurchaseOrderCreate(BaseModel):
    supplier_id: int = Field(..., gt=0, description="供应商ID")
    remark: Optional[str] = Field(None, description="备注")
    items: List[PurchaseOrderItemCreate] = Field(..., min_length=1, description="采购明细")


class PurchaseOrderItemResponse(BaseModel):
    id: int
    material_id: int
    quantity: Decimal
    unit_price: Optional[Decimal]
    received_qty: Decimal

    class Config:
        from_attributes = True


class PurchaseOrderResponse(BaseModel):
    id: int
    po_number: str
    supplier_id: int
    total_amount: Optional[Decimal]
    status: str
    remark: Optional[str]
    items: List[PurchaseOrderItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===========================================
# 工单 (WorkOrder) - ERP 创建
# ===========================================
class WorkOrderCreateRequest(BaseModel):
    product_id: int = Field(..., gt=0, description="成品ID")
    planned_quantity: int = Field(..., gt=0, description="计划生产数量")
    sales_order_id: Optional[int] = Field(None, description="关联销售订单ID")
    bom_id: Optional[int] = Field(None, description="关联BOM ID")
    remark: Optional[str] = Field(None, description="备注")


class WorkOrderCreateResponse(BaseModel):
    work_order_id: int
    work_order_number: str
    message: str
