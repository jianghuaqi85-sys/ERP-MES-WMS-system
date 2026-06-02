from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    username: Optional[str]
    action: str
    module: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[int]
    old_value: Optional[str]
    new_value: Optional[str]
    ip_address: Optional[str]
    remark: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_products: int
    total_materials: int
    total_work_orders: int
    pending_work_orders: int
    in_progress_work_orders: int
    completed_work_orders: int
    total_sales_orders: int
    pending_sales_orders: int
    total_suppliers: int
