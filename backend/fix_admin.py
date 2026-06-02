from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.apps.auth.models import User
from app.apps.auth.utils import get_password_hash

def fix_admin():
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(username="admin").first():
            db.add(User(username="admin", hashed_password=get_password_hash("123456"), role="ADMIN"))
            db.commit()
            print("Admin user restored.")
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin()
