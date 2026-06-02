from sqlalchemy import Column, String, Integer, Boolean
from app.core.database import Base
from app.core.models import TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "auth_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    role = Column(String(20), default="USER", nullable=False, comment="角色: ADMIN, WMS_USER, MES_USER")
    is_active = Column(Boolean, default=True, comment="是否启用")
