from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from sqlalchemy import text

def truncate_db():
    db = SessionLocal()
    try:
        db.execute(text("TRUNCATE TABLE erp_products CASCADE;"))
        db.execute(text("TRUNCATE TABLE wms_materials CASCADE;"))
        db.execute(text("TRUNCATE TABLE auth_users CASCADE;"))
        db.commit()
        print("Database truncated successfully.")
    except Exception as e:
        print(f"Error truncating data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    truncate_db()
