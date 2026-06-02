"""
种子数据脚本
用于初始化数据库基础数据
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.apps.auth.models import User
from app.apps.auth.utils import get_password_hash
from app.apps.wms.models import Material, Inventory
from app.apps.erp.models import Product, Supplier, BOM, BOMItem
from app.apps.mes.models import WorkOrder
from app.apps.traceability.models import TraceabilityRecord


def seed_data():
    db = SessionLocal()
    try:
        # ===========================================
        # 创建用户
        # ===========================================
        users_data = [
            ("admin", "123456", "ADMIN"),
            ("erp_user", "123456", "ERP_USER"),
            ("mes_user", "123456", "MES_USER"),
            ("wms_user", "123456", "WMS_USER"),
        ]
        for username, password, role in users_data:
            if not db.query(User).filter_by(username=username).first():
                db.add(User(
                    username=username,
                    hashed_password=get_password_hash(password),
                    role=role,
                ))
        db.commit()
        print("[OK] 用户数据创建完成")

        # ===========================================
        # 创建物料
        # ===========================================
        materials_data = [
            ("MAT-001", "屏幕面板", "pcs", "显示组件"),
            ("MAT-002", "A18 Pro 芯片", "pcs", "核心芯片"),
            ("MAT-003", "锂电池", "pcs", "电池组件"),
            ("MAT-004", "铝合金外壳", "pcs", "结构件"),
            ("MAT-005", "摄像头模组", "pcs", "光学组件"),
        ]
        for code, name, unit, category in materials_data:
            if not db.query(Material).filter_by(material_code=code).first():
                db.add(Material(
                    material_code=code,
                    name=name,
                    unit=unit,
                    category=category,
                    safety_stock=100,
                ))
        db.commit()
        print("[OK] 物料数据创建完成")

        # ===========================================
        # 创建产品
        # ===========================================
        products_data = [
            ("PRD-101", "iPhone 16 Pro", 8999.00, "pcs", "苹果旗舰手机"),
            ("PRD-102", "iPhone 16", 6999.00, "pcs", "苹果标准版手机"),
            ("PRD-103", "iPad Pro M4", 10999.00, "pcs", "苹果专业平板"),
        ]
        for code, name, price, unit, desc in products_data:
            if not db.query(Product).filter_by(product_code=code).first():
                db.add(Product(
                    product_code=code,
                    name=name,
                    price=price,
                    unit=unit,
                    description=desc,
                ))
        db.commit()
        print("[OK] 产品数据创建完成")

        # ===========================================
        # 创建供应商
        # ===========================================
        suppliers_data = [
            ("SUP-001", "深圳华星光电", "张三", "13800138001", "zhangsan@huaxing.com"),
            ("SUP-002", "台积电", "李四", "13800138002", "lisi@tsmc.com"),
            ("SUP-003", "宁德时代", "王五", "13800138003", "wangwu@catl.com"),
        ]
        for code, name, contact, phone, email in suppliers_data:
            if not db.query(Supplier).filter_by(code=code).first():
                db.add(Supplier(
                    code=code,
                    name=name,
                    contact_person=contact,
                    phone=phone,
                    email=email,
                    status="ACTIVE",
                ))
        db.commit()
        print("[OK] 供应商数据创建完成")

        # ===========================================
        # 创建 BOM
        # ===========================================
        product = db.query(Product).filter_by(product_code="PRD-101").first()
        if product and not db.query(BOM).filter_by(product_id=product.id).first():
            bom = BOM(
                product_id=product.id,
                version="1.0",
                is_default=True,
                status="ACTIVE",
                remark="iPhone 16 Pro 标准 BOM",
            )
            db.add(bom)
            db.flush()

            mat1 = db.query(Material).filter_by(material_code="MAT-001").first()
            mat2 = db.query(Material).filter_by(material_code="MAT-002").first()
            mat3 = db.query(Material).filter_by(material_code="MAT-003").first()
            mat4 = db.query(Material).filter_by(material_code="MAT-004").first()
            mat5 = db.query(Material).filter_by(material_code="MAT-005").first()

            bom_items = [
                (mat1, 1, "pcs"),
                (mat2, 1, "pcs"),
                (mat3, 1, "pcs"),
                (mat4, 1, "pcs"),
                (mat5, 2, "pcs"),
            ]
            for mat, qty, unit in bom_items:
                if mat:
                    db.add(BOMItem(
                        bom_id=bom.id,
                        material_id=mat.id,
                        quantity=qty,
                        unit=unit,
                    ))
            db.commit()
            print("[OK] BOM 数据创建完成")

        # ===========================================
        # 创建库存
        # ===========================================
        if not db.query(Inventory).first():
            m1 = db.query(Material).filter_by(material_code="MAT-001").first()
            m2 = db.query(Material).filter_by(material_code="MAT-002").first()
            m3 = db.query(Material).filter_by(material_code="MAT-003").first()
            m4 = db.query(Material).filter_by(material_code="MAT-004").first()
            m5 = db.query(Material).filter_by(material_code="MAT-005").first()

            inventories = [
                (m1, None, "A-01-01", 500, 0),
                (m2, None, "A-01-02", 200, 0),
                (m3, None, "A-02-01", 300, 0),
                (m4, None, "A-02-02", 400, 0),
                (m5, None, "A-03-01", 150, 0),
            ]
            for mat, prod, loc, avail, locked in inventories:
                if mat:
                    db.add(Inventory(
                        material_id=mat.id,
                        product_id=prod,
                        location_code=loc,
                        available_qty=avail,
                        locked_qty=locked,
                    ))
            db.commit()
            print("[OK] 库存数据创建完成")

        # ===========================================
        # 创建工单
        # ===========================================
        if not db.query(WorkOrder).first():
            wo = WorkOrder(
                work_order_number="WO-2026-001",
                product_id=product.id,
                planned_quantity=100,
                actual_quantity=100,
                qualified_quantity=98,
                defective_quantity=2,
                status="COMPLETED",
            )
            db.add(wo)
            db.commit()
            print("[OK] 工单数据创建完成")

        print("\n[DONE] 所有种子数据创建完成！")
        print("\n默认用户账号:")
        print("  admin / 123456 (管理员)")
        print("  erp_user / 123456 (ERP 用户)")
        print("  mes_user / 123456 (MES 用户)")
        print("  wms_user / 123456 (WMS 用户)")

    except Exception as e:
        print(f"[ERROR] 创建种子数据失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
