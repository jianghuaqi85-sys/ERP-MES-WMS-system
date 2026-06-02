import random
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.apps.erp.models import Product, Supplier, PurchaseOrder, PurchaseOrderItem, SalesOrder, BOM, BOMItem
from app.apps.wms.models import Material

def seed_erp():
    db = SessionLocal()
    try:
        # Get existing products and materials
        products = db.query(Product).all()
        materials = db.query(Material).all()

        if not products or not materials:
            print("No products or materials found. Run seed_massive first.")
            return

        # 1. Suppliers
        suppliers = []
        for i in range(1, 101):
            sup = Supplier(
                code=f"SUP-ENT-{i}",
                name=f"Enterprise Supplier {i} Co.",
                contact_person=f"Contact {i}",
                phone=f"1380000{i:04d}",
                email=f"sup{i}@example.com",
                address=f"Industrial Zone {i}"
            )
            db.add(sup)
            suppliers.append(sup)
        db.commit()
        for sup in suppliers: db.refresh(sup)

        # 2. Purchase Orders
        po_counter = 1000
        for _ in range(500):
            sup = random.choice(suppliers)
            po = PurchaseOrder(
                po_number=f"PO-{po_counter}",
                supplier_id=sup.id,
                status=random.choice(["DRAFT", "ISSUED", "RECEIVED"]),
                remark="Massive Seed PO"
            )
            db.add(po)
            db.commit()
            db.refresh(po)
            po_counter += 1
            
            # Add items
            total_amt = 0
            for _ in range(random.randint(1, 5)):
                mat = random.choice(materials)
                qty = random.randint(100, 5000)
                price = random.uniform(10.0, 500.0)
                total_amt += qty * price
                db.add(PurchaseOrderItem(
                    purchase_order_id=po.id,
                    material_id=mat.id,
                    quantity=qty,
                    unit_price=price,
                    received_qty=qty if po.status == "RECEIVED" else 0
                ))
            po.total_amount = total_amt
            db.commit()

        # 3. BOMs
        for prod in products:
            bom = BOM(
                product_id=prod.id,
                version="1.0",
                is_default=True,
                status="ACTIVE",
                remark="Standard Enterprise BOM"
            )
            db.add(bom)
            db.commit()
            db.refresh(bom)

            # Add BOM Items
            for _ in range(random.randint(2, 6)):
                mat = random.choice(materials)
                db.add(BOMItem(
                    bom_id=bom.id,
                    material_id=mat.id,
                    quantity=random.randint(1, 10),
                    unit="pcs"
                ))
            db.commit()

        # 4. Sales Orders
        so_counter = 5000
        for _ in range(1000):
            prod = random.choice(products)
            qty = random.randint(10, 1000)
            price = random.uniform(500.0, 2000.0)
            
            so = SalesOrder(
                order_number=f"SO-{so_counter}",
                customer_name=f"Enterprise Client {random.randint(1, 500)}",
                customer_contact=f"139000{random.randint(10000,99999)}",
                product_id=prod.id,
                quantity=qty,
                unit_price=price,
                total_amount=qty * price,
                status=random.choice(["DRAFT", "CONFIRMED", "SHIPPED", "COMPLETED"]),
                remark="Massive Seed SO"
            )
            db.add(so)
            so_counter += 1
        db.commit()

        print("ERP Data (Suppliers, POs, BOMs, SOs) seeded successfully!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_erp()
