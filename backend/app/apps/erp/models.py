from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.models import TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "erp_products"

    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True, index=True, nullable=False, comment="成品编码")
    name = Column(String(100), nullable=False, comment="成品名称")
    price = Column(Numeric(10, 2), nullable=False, default=0.0, comment="销售价格")
    unit = Column(String(20), default="pcs", comment="计量单位")
    description = Column(Text, comment="产品描述")

    # 关系
    sales_orders = relationship("SalesOrder", back_populates="product")
    boms = relationship("BOM", back_populates="product")


class SalesOrder(Base, TimestampMixin):
    __tablename__ = "erp_sales_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False, comment="销售单号")
    customer_name = Column(String(100), nullable=False, comment="客户名称")
    customer_contact = Column(String(100), comment="客户联系方式")
    product_id = Column(Integer, ForeignKey("erp_products.id"), nullable=False, comment="成品ID")
    quantity = Column(Integer, nullable=False, comment="销售数量")
    unit_price = Column(Numeric(10, 2), comment="单价")
    total_amount = Column(Numeric(12, 2), comment="总金额")
    status = Column(String(20), default="DRAFT", comment="状态")
    remark = Column(Text, comment="备注")

    # 关系
    product = relationship("Product", back_populates="sales_orders")


class BOM(Base, TimestampMixin):
    """物料清单 (Bill of Materials)"""
    __tablename__ = "erp_boms"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("erp_products.id"), nullable=False, comment="成品ID")
    version = Column(String(20), nullable=False, default="1.0", comment="BOM 版本")
    is_default = Column(Boolean, default=False, comment="是否默认版本")
    status = Column(String(20), default="DRAFT", comment="状态: DRAFT, ACTIVE, OBSOLETE")
    remark = Column(Text, comment="备注")

    # 关系
    product = relationship("Product", back_populates="boms")
    items = relationship("BOMItem", back_populates="bom", cascade="all, delete-orphan")


class BOMItem(Base, TimestampMixin):
    """BOM 子件明细"""
    __tablename__ = "erp_bom_items"

    id = Column(Integer, primary_key=True, index=True)
    bom_id = Column(Integer, ForeignKey("erp_boms.id"), nullable=False, comment="BOM ID")
    material_id = Column(Integer, ForeignKey("wms_materials.id"), nullable=False, comment="物料ID")
    quantity = Column(Numeric(10, 4), nullable=False, comment="单位用量")
    unit = Column(String(20), comment="单位")
    remark = Column(Text, comment="备注")

    # 关系
    bom = relationship("BOM", back_populates="items")
    material = relationship("Material")


class Supplier(Base, TimestampMixin):
    """供应商"""
    __tablename__ = "erp_suppliers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False, comment="供应商编码")
    name = Column(String(100), nullable=False, comment="供应商名称")
    contact_person = Column(String(50), comment="联系人")
    phone = Column(String(20), comment="电话")
    email = Column(String(100), comment="邮箱")
    address = Column(Text, comment="地址")
    status = Column(String(20), default="ACTIVE", comment="状态: ACTIVE, BLACKLISTED")

    # 关系
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")


class PurchaseOrder(Base, TimestampMixin):
    """采购订单"""
    __tablename__ = "erp_purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(50), unique=True, index=True, nullable=False, comment="采购单号")
    supplier_id = Column(Integer, ForeignKey("erp_suppliers.id"), nullable=False, comment="供应商ID")
    total_amount = Column(Numeric(12, 2), default=0, comment="总金额")
    status = Column(String(20), default="DRAFT", comment="状态")
    remark = Column(Text, comment="备注")

    # 关系
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base, TimestampMixin):
    """采购订单明细"""
    __tablename__ = "erp_purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("erp_purchase_orders.id"), nullable=False, comment="采购单ID")
    material_id = Column(Integer, ForeignKey("wms_materials.id"), nullable=False, comment="物料ID")
    quantity = Column(Numeric(10, 2), nullable=False, comment="采购数量")
    unit_price = Column(Numeric(10, 2), comment="单价")
    received_qty = Column(Numeric(10, 2), default=0, comment="已收货数量")

    # 关系
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    material = relationship("Material")
