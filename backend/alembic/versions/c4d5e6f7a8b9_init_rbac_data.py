"""Init RBAC data

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-06-12 00:20:00.000000

"""
from typing import Sequence, Union
from datetime import datetime, timezone
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c4d5e6f7a8b9'
down_revision: Union[str, None] = 'b3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Create missing RBAC tables
    op.create_table('auth_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False, comment='权限标识，例如 product:read'),
        sa.Column('description', sa.String(length=255), nullable=True, comment='权限描述'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_auth_permissions_id'), 'auth_permissions', ['id'], unique=False)

    op.create_table('auth_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False, comment='角色名称，例如 ADMIN'),
        sa.Column('description', sa.String(length=255), nullable=True, comment='角色描述'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_auth_roles_id'), 'auth_roles', ['id'], unique=False)

    op.create_table('role_permission',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['auth_permissions.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['auth_roles.id'], ),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

    op.create_table('user_role',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['auth_roles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['auth_users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # 1. Insert default permissions
    permissions = [
        {"name": "admin:*", "description": "Administrator all permissions"},
        {"name": "erp:read", "description": "Read ERP data"},
        {"name": "erp:write", "description": "Write/Modify ERP data"},
        {"name": "mes:read", "description": "Read MES data"},
        {"name": "mes:write", "description": "Write/Modify MES data"},
        {"name": "wms:read", "description": "Read WMS data"},
        {"name": "wms:write", "description": "Write/Modify WMS data"},
    ]
    
    permissions_table = sa.table(
        'auth_permissions',
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime)
    )
    
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for perm in permissions:
        perm['created_at'] = now
        perm['updated_at'] = now
        
    op.bulk_insert(permissions_table, permissions)
    
    # 2. Insert default roles
    roles = [
        {"name": "ADMIN", "description": "System Administrator"},
        {"name": "ERP_USER", "description": "ERP Operator"},
        {"name": "MES_USER", "description": "MES Operator"},
        {"name": "WMS_USER", "description": "WMS Operator"},
    ]
    
    roles_table = sa.table(
        'auth_roles',
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime)
    )
    
    for r in roles:
        r['created_at'] = now
        r['updated_at'] = now
        
    op.bulk_insert(roles_table, roles)
    
    # 3. Associate roles and permissions
    conn = op.get_bind()
    
    # Query permissions and roles to get their auto-generated IDs
    perms_res = conn.execute(sa.text("SELECT id, name FROM auth_permissions")).fetchall()
    roles_res = conn.execute(sa.text("SELECT id, name FROM auth_roles")).fetchall()
    
    perm_map = {name: id_ for id_, name in perms_res}
    role_map = {name: id_ for id_, name in roles_res}
    
    role_permissions = []
    
    # ADMIN gets admin:*
    if "ADMIN" in role_map and "admin:*" in perm_map:
        role_permissions.append({"role_id": role_map["ADMIN"], "permission_id": perm_map["admin:*"]})
        
    # ERP_USER gets erp:read, erp:write
    if "ERP_USER" in role_map:
        for p in ["erp:read", "erp:write"]:
            if p in perm_map:
                role_permissions.append({"role_id": role_map["ERP_USER"], "permission_id": perm_map[p]})
                
    # MES_USER gets mes:read, mes:write
    if "MES_USER" in role_map:
        for p in ["mes:read", "mes:write"]:
            if p in perm_map:
                role_permissions.append({"role_id": role_map["MES_USER"], "permission_id": perm_map[p]})
                
    # WMS_USER gets wms:read, wms:write
    if "WMS_USER" in role_map:
        for p in ["wms:read", "wms:write"]:
            if p in perm_map:
                role_permissions.append({"role_id": role_map["WMS_USER"], "permission_id": perm_map[p]})
                
    role_permission_table = sa.table(
        'role_permission',
        sa.column('role_id', sa.Integer),
        sa.column('permission_id', sa.Integer)
    )
    op.bulk_insert(role_permission_table, role_permissions)


def downgrade() -> None:
    # Drop tables
    op.drop_table('user_role')
    op.drop_table('role_permission')
    op.drop_index(op.f('ix_auth_roles_id'), table_name='auth_roles')
    op.drop_table('auth_roles')
    op.drop_index(op.f('ix_auth_permissions_id'), table_name='auth_permissions')
    op.drop_table('auth_permissions')
