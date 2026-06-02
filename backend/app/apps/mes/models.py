from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.models import TimestampMixin


class WorkOrder(Base, TimestampMixin):
    __tablename__ = "mes_work_orders"

    id = Column(Integer, primary_key=True, index=True)
    work_order_number = Column(String(50), unique=True, index=True, nullable=False, comment="生产工单号")
    sales_order_id = Column(Integer, ForeignKey("erp_sales_orders.id"), nullable=True, comment="关联销售订单ID")
    bom_id = Column(Integer, ForeignKey("erp_boms.id"), nullable=True, comment="关联BOM ID")
    product_id = Column(Integer, ForeignKey("erp_products.id"), nullable=False, comment="目标成品ID")
    planned_quantity = Column(Integer, nullable=False, comment="计划生产数量")
    actual_quantity = Column(Integer, default=0, comment="实际产出数量")
    qualified_quantity = Column(Integer, default=0, comment="合格数量")
    defective_quantity = Column(Integer, default=0, comment="不良数量")
    status = Column(String(20), default="PLANNED", comment="状态")
    planned_start = Column(DateTime, comment="计划开始时间")
    planned_end = Column(DateTime, comment="计划结束时间")
    actual_start = Column(DateTime, comment="实际开始时间")
    actual_end = Column(DateTime, comment="实际结束时间")
    remark = Column(Text, comment="备注")

    # 关系
    processes = relationship("WorkOrderProcess", back_populates="work_order", cascade="all, delete-orphan")


class WorkOrderProcess(Base, TimestampMixin):
    """工单工序"""
    __tablename__ = "mes_work_order_processes"

    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("mes_work_orders.id"), nullable=False, comment="工单ID")
    process_name = Column(String(50), nullable=False, comment="工序名称")
    sequence = Column(Integer, nullable=False, comment="工序顺序")
    status = Column(String(20), default="PENDING", comment="状态: PENDING, IN_PROGRESS, COMPLETED")
    planned_start = Column(DateTime, comment="计划开始时间")
    planned_end = Column(DateTime, comment="计划结束时间")
    actual_start = Column(DateTime, comment="实际开始时间")
    actual_end = Column(DateTime, comment="实际结束时间")
    remark = Column(Text, comment="备注")

    # 关系
    work_order = relationship("WorkOrder", back_populates="processes")
