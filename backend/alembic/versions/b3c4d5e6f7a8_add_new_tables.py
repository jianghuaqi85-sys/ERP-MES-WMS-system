"""Add new tables for ERP-MES-WMS

Revision ID: b3c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-06-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 修改 erp_products 表 - 添加新字段
    op.add_column('erp_products', sa.Column('unit', sa.String(length=20), nullable=True, comment='计量单位'))
    op.add_column('erp_products', sa.Column('description', sa.Text(), nullable=True, comment='产品描述'))
    op.alter_column('erp_products', 'price', type_=sa.Numeric(10, 2))

    # 修改 erp_sales_orders 表 - 添加新字段
    op.add_column('erp_sales_orders', sa.Column('customer_contact', sa.String(length=100), nullable=True, comment='客户联系方式'))
    op.add_column('erp_sales_orders', sa.Column('unit_price', sa.Numeric(10, 2), nullable=True, comment='单价'))
    op.add_column('erp_sales_orders', sa.Column('total_amount', sa.Numeric(12, 2), nullable=True, comment='总金额'))
    op.add_column('erp_sales_orders', sa.Column('remark', sa.Text(), nullable=True, comment='备注'))

    # 修改 wms_materials 表 - 添加新字段
    op.add_column('wms_materials', sa.Column('category', sa.String(length=50), nullable=True, comment='物料分类'))
    op.add_column('wms_materials', sa.Column('safety_stock', sa.Integer(), nullable=True, comment='安全库存'))
    op.add_column('wms_materials', sa.Column('description', sa.Text(), nullable=True, comment='描述'))

    # 修改 wms_inventories 表 - 添加批次号
    op.add_column('wms_inventories', sa.Column('batch_number', sa.String(length=50), nullable=True, comment='批次号'))

    # 修改 mes_work_orders 表 - 添加新字段
    op.add_column('mes_work_orders', sa.Column('sales_order_id', sa.Integer(), nullable=True, comment='关联销售订单ID'))
    op.add_column('mes_work_orders', sa.Column('bom_id', sa.Integer(), nullable=True, comment='关联BOM ID'))
    op.add_column('mes_work_orders', sa.Column('qualified_quantity', sa.Integer(), nullable=True, comment='合格数量'))
    op.add_column('mes_work_orders', sa.Column('defective_quantity', sa.Integer(), nullable=True, comment='不良数量'))
    op.add_column('mes_work_orders', sa.Column('planned_start', sa.DateTime(), nullable=True, comment='计划开始时间'))
    op.add_column('mes_work_orders', sa.Column('planned_end', sa.DateTime(), nullable=True, comment='计划结束时间'))
    op.add_column('mes_work_orders', sa.Column('actual_start', sa.DateTime(), nullable=True, comment='实际开始时间'))
    op.add_column('mes_work_orders', sa.Column('actual_end', sa.DateTime(), nullable=True, comment='实际结束时间'))
    op.add_column('mes_work_orders', sa.Column('remark', sa.Text(), nullable=True, comment='备注'))
    op.create_foreign_key('fk_mes_work_orders_sales_order', 'mes_work_orders', 'erp_sales_orders', ['sales_order_id'], ['id'])

    # 创建 erp_boms 表
    op.create_table('erp_boms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False, comment='成品ID'),
        sa.Column('version', sa.String(length=20), nullable=False, comment='BOM 版本'),
        sa.Column('is_default', sa.Boolean(), nullable=True, comment='是否默认版本'),
        sa.Column('status', sa.String(length=20), nullable=True, comment='状态: DRAFT, ACTIVE, OBSOLETE'),
        sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.ForeignKeyConstraint(['product_id'], ['erp_products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_erp_boms_id'), 'erp_boms', ['id'], unique=False)

    # 创建 erp_bom_items 表
    op.create_table('erp_bom_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bom_id', sa.Integer(), nullable=False, comment='BOM ID'),
        sa.Column('material_id', sa.Integer(), nullable=False, comment='物料ID'),
        sa.Column('quantity', sa.Numeric(10, 4), nullable=False, comment='单位用量'),
        sa.Column('unit', sa.String(length=20), nullable=True, comment='单位'),
        sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.ForeignKeyConstraint(['bom_id'], ['erp_boms.id'], ),
        sa.ForeignKeyConstraint(['material_id'], ['wms_materials.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_erp_bom_items_id'), 'erp_bom_items', ['id'], unique=False)

    # 添加 BOM 外键到 mes_work_orders
    op.create_foreign_key('fk_mes_work_orders_bom', 'mes_work_orders', 'erp_boms', ['bom_id'], ['id'])

    # 创建 erp_suppliers 表
    op.create_table('erp_suppliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False, comment='供应商编码'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='供应商名称'),
        sa.Column('contact_person', sa.String(length=50), nullable=True, comment='联系人'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='电话'),
        sa.Column('email', sa.String(length=100), nullable=True, comment='邮箱'),
        sa.Column('address', sa.Text(), nullable=True, comment='地址'),
        sa.Column('status', sa.String(length=20), nullable=True, comment='状态: ACTIVE, BLACKLISTED'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_erp_suppliers_id'), 'erp_suppliers', ['id'], unique=False)
    op.create_index(op.f('ix_erp_suppliers_code'), 'erp_suppliers', ['code'], unique=True)

    # 创建 erp_purchase_orders 表
    op.create_table('erp_purchase_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('po_number', sa.String(length=50), nullable=False, comment='采购单号'),
        sa.Column('supplier_id', sa.Integer(), nullable=False, comment='供应商ID'),
        sa.Column('total_amount', sa.Numeric(12, 2), nullable=True, comment='总金额'),
        sa.Column('status', sa.String(length=20), nullable=True, comment='状态'),
        sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.ForeignKeyConstraint(['supplier_id'], ['erp_suppliers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_erp_purchase_orders_id'), 'erp_purchase_orders', ['id'], unique=False)
    op.create_index(op.f('ix_erp_purchase_orders_po_number'), 'erp_purchase_orders', ['po_number'], unique=True)

    # 创建 erp_purchase_order_items 表
    op.create_table('erp_purchase_order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('purchase_order_id', sa.Integer(), nullable=False, comment='采购单ID'),
        sa.Column('material_id', sa.Integer(), nullable=False, comment='物料ID'),
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False, comment='采购数量'),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=True, comment='单价'),
        sa.Column('received_qty', sa.Numeric(10, 2), nullable=True, comment='已收货数量'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.ForeignKeyConstraint(['material_id'], ['wms_materials.id'], ),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['erp_purchase_orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_erp_purchase_order_items_id'), 'erp_purchase_order_items', ['id'], unique=False)

    # 创建 mes_work_order_processes 表
    op.create_table('mes_work_order_processes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('work_order_id', sa.Integer(), nullable=False, comment='工单ID'),
        sa.Column('process_name', sa.String(length=50), nullable=False, comment='工序名称'),
        sa.Column('sequence', sa.Integer(), nullable=False, comment='工序顺序'),
        sa.Column('status', sa.String(length=20), nullable=True, comment='状态: PENDING, IN_PROGRESS, COMPLETED'),
        sa.Column('planned_start', sa.DateTime(), nullable=True, comment='计划开始时间'),
        sa.Column('planned_end', sa.DateTime(), nullable=True, comment='计划结束时间'),
        sa.Column('actual_start', sa.DateTime(), nullable=True, comment='实际开始时间'),
        sa.Column('actual_end', sa.DateTime(), nullable=True, comment='实际结束时间'),
        sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.ForeignKeyConstraint(['work_order_id'], ['mes_work_orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mes_work_order_processes_id'), 'mes_work_order_processes', ['id'], unique=False)

    # 创建 wms_inventory_transactions 表
    op.create_table('wms_inventory_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inventory_id', sa.Integer(), nullable=False, comment='库存记录ID'),
        sa.Column('transaction_type', sa.String(length=20), nullable=False, comment='变动类型'),
        sa.Column('quantity', sa.Integer(), nullable=False, comment='变动数量'),
        sa.Column('reference_type', sa.String(length=50), nullable=True, comment='关联单据类型'),
        sa.Column('reference_id', sa.Integer(), nullable=True, comment='关联单据ID'),
        sa.Column('operator_id', sa.Integer(), nullable=True, comment='操作人ID'),
        sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.ForeignKeyConstraint(['inventory_id'], ['wms_inventories.id'], ),
        sa.ForeignKeyConstraint(['operator_id'], ['auth_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wms_inventory_transactions_id'), 'wms_inventory_transactions', ['id'], unique=False)

    # 创建 wms_warehouse_locations 表
    op.create_table('wms_warehouse_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('warehouse_code', sa.String(length=20), nullable=False, comment='仓库编码'),
        sa.Column('zone_code', sa.String(length=20), nullable=True, comment='库区编码'),
        sa.Column('shelf_code', sa.String(length=20), nullable=True, comment='货架编码'),
        sa.Column('layer_code', sa.String(length=10), nullable=True, comment='层编码'),
        sa.Column('position_code', sa.String(length=10), nullable=True, comment='位编码'),
        sa.Column('capacity', sa.Integer(), nullable=True, comment='容量'),
        sa.Column('status', sa.String(length=20), nullable=True, comment='状态: ACTIVE, DISABLED'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wms_warehouse_locations_id'), 'wms_warehouse_locations', ['id'], unique=False)

    # 创建 system_audit_logs 表
    op.create_table('system_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True, comment='操作用户ID'),
        sa.Column('username', sa.String(length=50), nullable=True, comment='操作用户名'),
        sa.Column('action', sa.String(length=50), nullable=False, comment='操作类型'),
        sa.Column('module', sa.String(length=50), nullable=True, comment='模块'),
        sa.Column('resource_type', sa.String(length=50), nullable=True, comment='资源类型'),
        sa.Column('resource_id', sa.Integer(), nullable=True, comment='资源ID'),
        sa.Column('old_value', sa.Text(), nullable=True, comment='变更前值'),
        sa.Column('new_value', sa.Text(), nullable=True, comment='变更后值'),
        sa.Column('ip_address', sa.String(length=50), nullable=True, comment='IP地址'),
        sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_audit_logs_id'), 'system_audit_logs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('system_audit_logs')
    op.drop_table('wms_warehouse_locations')
    op.drop_table('wms_inventory_transactions')
    op.drop_table('mes_work_order_processes')
    op.drop_table('erp_purchase_order_items')
    op.drop_table('erp_purchase_orders')
    op.drop_table('erp_suppliers')
    op.drop_table('erp_bom_items')
    op.drop_table('erp_boms')

    op.drop_column('mes_work_orders', 'remark')
    op.drop_column('mes_work_orders', 'actual_end')
    op.drop_column('mes_work_orders', 'actual_start')
    op.drop_column('mes_work_orders', 'planned_end')
    op.drop_column('mes_work_orders', 'planned_start')
    op.drop_column('mes_work_orders', 'defective_quantity')
    op.drop_column('mes_work_orders', 'qualified_quantity')
    op.drop_column('mes_work_orders', 'bom_id')
    op.drop_column('mes_work_orders', 'sales_order_id')

    op.drop_column('wms_inventories', 'batch_number')

    op.drop_column('wms_materials', 'description')
    op.drop_column('wms_materials', 'safety_stock')
    op.drop_column('wms_materials', 'category')

    op.drop_column('erp_sales_orders', 'remark')
    op.drop_column('erp_sales_orders', 'total_amount')
    op.drop_column('erp_sales_orders', 'unit_price')
    op.drop_column('erp_sales_orders', 'customer_contact')

    op.drop_column('erp_products', 'description')
    op.drop_column('erp_products', 'unit')
