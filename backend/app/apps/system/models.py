from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base
from app.core.models import TimestampMixin


class AuditLog(Base, TimestampMixin):
    """操作审计日志"""
    __tablename__ = "system_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, comment="操作用户ID")
    username = Column(String(50), comment="操作用户名")
    action = Column(String(50), nullable=False, comment="操作类型: CREATE, UPDATE, DELETE, LOGIN, etc.")
    module = Column(String(50), comment="模块: auth, erp, mes, wms, system")
    resource_type = Column(String(50), comment="资源类型: product, work_order, etc.")
    resource_id = Column(Integer, comment="资源ID")
    old_value = Column(Text, comment="变更前值(JSON)")
    new_value = Column(Text, comment="变更后值(JSON)")
    ip_address = Column(String(50), comment="IP地址")
    remark = Column(Text, comment="备注")
