import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.apps.auth.models import User
from app.apps.erp.models import Product
from app.apps.wms.models import Material, Inventory
from app.apps.mes.models import WorkOrder
from app.apps.traceability.models import TraceabilityRecord

def seed_massive():
    db = SessionLocal()
    try:
        # Generate 200 products
        db_products = []
        for i in range(200):
            p = Product(name=f"Enterprise Product Series {i}", product_code=f"PRD-ENT-{1000+i}")
            db.add(p)
            db_products.append(p)
        db.commit()
        for p in db_products: db.refresh(p)

        # Generate 1000 materials
        db_materials = []
        for i in range(1000):
            m = Material(name=f"Raw Material Type {i}", material_code=f"MAT-RAW-{10000+i}", unit="pcs")
            db.add(m)
            db_materials.append(m)
        db.commit()
        for m in db_materials: db.refresh(m)

        # Generate Inventory (lots of it)
        locations = [f"Z{z}-R{r}-S{s}" for z in range(1, 10) for r in range(1, 10) for s in range(1, 10)]
        for i, m in enumerate(db_materials):
            for _ in range(random.randint(1, 5)):
                inv = Inventory(
                    material_id=m.id,
                    location_code=random.choice(locations),
                    available_qty=random.randint(100, 10000),
                    locked_qty=random.randint(0, 100)
                )
                db.add(inv)
        db.commit()

        # Generate 5000 Work Orders
        statuses = ["PLANNED", "IN_PROGRESS", "COMPLETED"]
        db_wos = []
        wo_counter = 10000
        for _ in range(5000):
            p = random.choice(db_products)
            planned = random.randint(50, 5000)
            status = random.choices(statuses, weights=[0.2, 0.3, 0.5])[0]
            actual = 0
            if status == "COMPLETED": actual = planned
            elif status == "IN_PROGRESS": actual = random.randint(1, planned - 1)
            
            wo = WorkOrder(
                work_order_number=f"WO-{wo_counter}",
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

        # Generate some traceability for the first 100 completed work orders to avoid making generation too slow
        completed_wos = [wo for wo in db_wos if wo.status == "COMPLETED"][:100]
        for wo in completed_wos:
            p = next(prod for prod in db_products if prod.id == wo.product_id)
            for sn_idx in range(1, 3):
                product_sn = f"{p.product_code}-SN-{wo.id}-{sn_idx}"
                used_mats = random.sample(db_materials, random.randint(2, 5))
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
        print("Massive data seeded successfully.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_massive()
