from sqlalchemy import Column, String, Integer, ForeignKey
from app.core.database import Base
from app.core.models import TimestampMixin

class TraceabilityRecord(Base, TimestampMixin):
    __tablename__ = "traceability_records"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 这里的source和target可以使用多态或者松耦合的字符串关联，为了清晰使用表名+ID
    source_type = Column(String(50), nullable=False, comment="来源类型(如 MATERIAL, PRODUCT)")
    source_id = Column(Integer, nullable=False, comment="来源记录ID")
    source_barcode = Column(String(100), nullable=True, comment="来源条码/批次号(具体到物理实物)")
    
    target_type = Column(String(50), nullable=False, comment="目标类型(如 PRODUCT)")
    target_id = Column(Integer, nullable=False, comment="目标记录ID")
    target_barcode = Column(String(100), nullable=True, comment="目标条码/批次号")
    
    work_order_id = Column(Integer, ForeignKey("mes_work_orders.id"), nullable=True, comment="关联生产工单")
    action_type = Column(String(50), nullable=False, comment="动作(如 ASSEMBLE, REPACK)")
