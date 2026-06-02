"""
业务常量定义
将散布在各模块中的魔法字符串统一管理
"""


class WorkOrderStatus:
    """工单状态"""
    PLANNED = "PLANNED"
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"


class SalesOrderStatus:
    """销售单状态"""
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    IN_PRODUCTION = "IN_PRODUCTION"
    READY_TO_SHIP = "READY_TO_SHIP"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class BOMStatus:
    """BOM 状态"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    OBSOLETE = "OBSOLETE"


class PurchaseOrderStatus:
    """采购订单状态"""
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class SupplierStatus:
    """供应商状态"""
    ACTIVE = "ACTIVE"
    BLACKLISTED = "BLACKLISTED"


class TraceSourceType:
    """溯源来源类型"""
    MATERIAL = "MATERIAL"


class TraceTargetType:
    """溯源目标类型"""
    PRODUCT = "PRODUCT"


class TraceActionType:
    """溯源动作类型"""
    ASSEMBLE = "ASSEMBLE"
    REPACK = "REPACK"


class InventoryLocation:
    """固定库位编码"""
    FINISHED_GOODS = "FINISHED_GOODS"


class UserRole:
    """用户角色"""
    ADMIN = "ADMIN"
    USER = "USER"
    ERP_USER = "ERP_USER"
    WMS_USER = "WMS_USER"
    MES_USER = "MES_USER"


class InventoryTransactionType:
    """库存变动类型"""
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER = "TRANSFER"
