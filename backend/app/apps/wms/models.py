from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.models import TimestampMixin


class Material(Base, TimestampMixin):
    __tablename__ = "wms_materials"

    id = Column(Integer, primary_key=True, index=True)
    material_code = Column(String(50), unique=True, index=True, nullable=False, comment="物料编码")
    name = Column(String(100), nullable=False, comment="物料名称")
    unit = Column(String(20), nullable=False, comment="计量单位(kg, pcs)")
    category = Column(String(50), comment="物料分类")
    safety_stock = Column(Integer, default=0, comment="安全库存")
    description = Column(Text, comment="描述")

    # 关系
    inventories = relationship("Inventory", back_populates="material")


class Inventory(Base, TimestampMixin):
    __tablename__ = "wms_inventories"
    __table_args__ = (
        CheckConstraint("available_qty >= 0", name="ck_inventory_available_qty_non_negative"),
        CheckConstraint("locked_qty >= 0", name="ck_inventory_locked_qty_non_negative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("wms_materials.id"), nullable=True, comment="关联物料ID(如果是原材料)")
    product_id = Column(Integer, ForeignKey("erp_products.id"), nullable=True, comment="关联成品ID(如果是产成品)")
    location_code = Column(String(50), nullable=False, comment="库位号")
    batch_number = Column(String(50), comment="批次号")
    available_qty = Column(Integer, default=0, nullable=False, comment="可用库存数量")
    locked_qty = Column(Integer, default=0, nullable=False, comment="锁定库存数量(生产预扣)")

    # 关系
    material = relationship("Material", back_populates="inventories")


class InventoryTransaction(Base, TimestampMixin):
    """库存变动日志"""
    __tablename__ = "wms_inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("wms_inventories.id"), nullable=False, comment="库存记录ID")
    transaction_type = Column(String(20), nullable=False, comment="变动类型: INBOUND, OUTBOUND, ADJUSTMENT, TRANSFER")
    quantity = Column(Integer, nullable=False, comment="变动数量(正数入库，负数出库)")
    reference_type = Column(String(50), comment="关联单据类型")
    reference_id = Column(Integer, comment="关联单据ID")
    operator_id = Column(Integer, ForeignKey("auth_users.id"), comment="操作人ID")
    remark = Column(Text, comment="备注")

    # 关系
    inventory = relationship("Inventory")


class WarehouseLocation(Base, TimestampMixin):
    """库位管理"""
    __tablename__ = "wms_warehouse_locations"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_code = Column(String(20), nullable=False, comment="仓库编码")
    zone_code = Column(String(20), comment="库区编码")
    shelf_code = Column(String(20), comment="货架编码")
    layer_code = Column(String(10), comment="层编码")
    position_code = Column(String(10), comment="位编码")
    capacity = Column(Integer, comment="容量")
    status = Column(String(20), default="ACTIVE", comment="状态: ACTIVE, DISABLED")
