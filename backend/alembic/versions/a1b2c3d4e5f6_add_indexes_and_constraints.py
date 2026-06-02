"""Add indexes and constraints

Revision ID: a1b2c3d4e5f6
Revises: 2fbee84216cd
Create Date: 2026-06-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '2fbee84216cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 溯源表添加复合索引，加速按条码+类型查询
    op.create_index(
        'ix_traceability_target_barcode_type',
        'traceability_records',
        ['target_barcode', 'target_type'],
    )

    # 2. 库存表添加非负约束
    op.create_check_constraint(
        'ck_inventory_available_qty_non_negative',
        'wms_inventories',
        'available_qty >= 0',
    )
    op.create_check_constraint(
        'ck_inventory_locked_qty_non_negative',
        'wms_inventories',
        'locked_qty >= 0',
    )


def downgrade() -> None:
    op.drop_constraint('ck_inventory_locked_qty_non_negative', 'wms_inventories', type_='check')
    op.drop_constraint('ck_inventory_available_qty_non_negative', 'wms_inventories', type_='check')
    op.drop_index('ix_traceability_target_barcode_type', table_name='traceability_records')
