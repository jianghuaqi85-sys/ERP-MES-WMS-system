import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.apps.auth.models import User
from app.apps.auth.utils import get_password_hash
from app.apps.erp.models import Product
from app.apps.wms.models import Material, Inventory
from app.apps.mes.models import WorkOrder
from app.apps.traceability.models import TraceabilityRecord

def seed_bulk():
    db = SessionLocal()
    try:
        # 1. 确保 Admin 存在
        if not db.query(User).filter_by(username="admin").first():
            db.add(User(username="admin", hashed_password=get_password_hash("123456"), role="ADMIN"))
            db.commit()

        # 2. 清理旧数据 (为了重新灌入大量新数据)
        db.query(TraceabilityRecord).delete()
        db.query(WorkOrder).delete()
        db.query(Inventory).delete()
        db.query(Product).delete()
        db.query(Material).delete()
        db.commit()

        # 3. 制造真实感的产品数据 (ERP)
        products_data = [
            ("iPhone 16 Pro Max", "PRD-APL-16PM"),
            ("MacBook Pro M4 14-inch", "PRD-APL-MBP14"),
            ("Tesla Model 3 Highland", "PRD-TSL-M3H"),
            ("DJI Mavic 4 Pro", "PRD-DJI-M4P"),
            ("Sony PlayStation 5 Pro", "PRD-SNY-PS5P")
        ]
        db_products = []
        for name, code in products_data:
            p = Product(name=name, product_code=code)
            db.add(p)
            db_products.append(p)
        db.commit()
        for p in db_products: db.refresh(p)

        # 4. 制造真实感的物料数据 (WMS)
        materials_data = [
            ("OLED Display 6.9 inch", "MAT-SCR-001"),
            ("A18 Pro Bionic Chip", "MAT-CHP-001"),
            ("M4 Max Silicon Chip", "MAT-CHP-002"),
            ("Liquid Retina XDR Display", "MAT-SCR-002"),
            ("LFP Battery Pack 60kWh", "MAT-BAT-001"),
            ("Electric Motor (Rear)", "MAT-MOT-001"),
            ("Carbon Fiber Propellers", "MAT-PRP-001"),
            ("4K Hasselblad Camera Module", "MAT-CAM-001"),
            ("AMD Zen 2 Custom APU", "MAT-CHP-003"),
            ("DualSense Wireless Controller", "MAT-ACC-001"),
            ("Titanium Alloy Frame", "MAT-FRM-001"),
            ("Lithium-ion Battery 4676mAh", "MAT-BAT-002"),
            ("NAND Flash Memory 1TB", "MAT-MEM-001"),
            ("LPDDR5X RAM 16GB", "MAT-RAM-001")
        ]
        db_materials = []
        for name, code in materials_data:
            m = Material(name=name, material_code=code, unit="pcs")
            db.add(m)
            db_materials.append(m)
        db.commit()
        for m in db_materials: db.refresh(m)

        # 5. 制造库存数据 (WMS Inventory)
        locations = [f"{zone}-{str(rack).zfill(2)}-{str(shelf).zfill(2)}" for zone in "ABCDEF" for rack in range(1, 6) for shelf in range(1, 6)]
        for i, m in enumerate(db_materials):
            # 每个物料随机分布在 2 到 4 个不同的库位中
            for _ in range(random.randint(2, 4)):
                inv = Inventory(
                    material_id=m.id,
                    location_code=random.choice(locations),
                    available_qty=random.randint(50, 5000),
                    locked_qty=random.randint(0, 50)
                )
                db.add(inv)
        db.commit()

        # 6. 制造生产工单数据 (MES)
        # 为每个产品生成不同状态的工单
        statuses = ["PLANNED", "IN_PROGRESS", "COMPLETED"]
        db_wos = []
        wo_counter = 1000
        for p in db_products:
            for _ in range(random.randint(3, 8)):
                planned = random.randint(100, 1000)
                status = random.choice(statuses)
                actual = 0
                if status == "COMPLETED": actual = planned
                elif status == "IN_PROGRESS": actual = random.randint(1, planned - 1)
                
                wo = WorkOrder(
                    work_order_number=f"WO-2026-{wo_counter}",
                    product_id=p.id,
                    planned_quantity=planned,
                    actual_quantity=actual,
                    status=status
                )
                db.add(wo)
                db_wos.append(wo)
                wo_counter += 1
        db.commit()
        for wo in db_wos: db.refresh(wo)

        # 7. 制造极为复杂的全链路溯源图谱数据 (Traceability)
        # 挑选已完成的工单，生成溯源链路
        completed_wos = [wo for wo in db_wos if wo.status == "COMPLETED"]
        for wo in completed_wos:
            p = next(prod for prod in db_products if prod.id == wo.product_id)
            
            # 为该工单生成3个具体的产成品序列号
            for sn_idx in range(1, 4):
                product_sn = f"{p.product_code}-SN-{wo.id}-{sn_idx}"
                
                # 随机选择 2~4 种物料作为原材料
                used_mats = random.sample(db_materials, random.randint(2, 4))
                
                for m in used_mats:
                    batch_no = f"{m.material_code}-BATCH-{random.randint(1000, 9999)}"
                    db.add(TraceabilityRecord(
                        source_id=m.id,
                        source_barcode=batch_no,
                        source_type="MATERIAL",
                        target_id=p.id,
                        target_barcode=product_sn,
                        target_type="PRODUCT",
                        work_order_id=wo.id,
                        action_type="CONSUME"
                    ))
        db.commit()
        print("Bulk realistic data seeded successfully! 🚀")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_bulk()
