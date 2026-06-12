from sqlalchemy import Column, String, Integer, Boolean
from app.core.database import Base
from app.core.models import TimestampMixin
from sqlalchemy import Table, ForeignKey
from sqlalchemy.orm import relationship
class User(Base, TimestampMixin):
    __tablename__ = "auth_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    role = Column(String(20), default="USER", nullable=False, comment="角色: ADMIN, WMS_USER, MES_USER")
    is_active = Column(Boolean, default=True, comment="是否启用")
    roles = relationship('Role', secondary='user_role', back_populates='users')

# RBAC association tables
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column('role_id', Integer, ForeignKey('auth_roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('auth_permissions.id'), primary_key=True),
)

user_role = Table(
    "user_role",
    Base.metadata,
    Column('user_id', Integer, ForeignKey('auth_users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('auth_roles.id'), primary_key=True),
)

class Permission(Base, TimestampMixin):
    __tablename__ = "auth_permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="权限标识，例如 product:read")
    description = Column(String(255), nullable=True, comment="权限描述")

class Role(Base, TimestampMixin):
    __tablename__ = "auth_roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="角色名称，例如 ADMIN")
    description = Column(String(255), nullable=True, comment="角色描述")
    permissions = relationship('Permission', secondary=role_permission, back_populates='roles')
    users = relationship('User', secondary=user_role, back_populates='roles')

Permission.roles = relationship('Role', secondary=role_permission, back_populates='permissions')
