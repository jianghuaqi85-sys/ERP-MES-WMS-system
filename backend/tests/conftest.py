import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.apps.auth.models import User, Role, Permission

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Seed default roles & permissions
        roles = {}
        for role_name in ["ADMIN", "ERP_USER", "MES_USER", "WMS_USER"]:
            role = Role(name=role_name, description=f"{role_name} Role")
            db.add(role)
            roles[role_name] = role
            
        perms = {}
        for perm_name in ["admin:*", "erp:read", "erp:write", "mes:read", "mes:write", "wms:read", "wms:write"]:
            perm = Permission(name=perm_name, description=f"{perm_name} Permission")
            db.add(perm)
            perms[perm_name] = perm
            
        db.commit()
        
        # Link roles to permissions
        roles["ADMIN"].permissions.append(perms["admin:*"])
        roles["ERP_USER"].permissions.extend([perms["erp:read"], perms["erp:write"]])
        roles["MES_USER"].permissions.extend([perms["mes:read"], perms["mes:write"]])
        roles["WMS_USER"].permissions.extend([perms["wms:read"], perms["wms:write"]])
        
        # Create users
        # For simple auth testing, we will mock get_current_user or seed them with hashed password
        # To avoid bcrypt slowness in tests, we can just seed their roles and usernames
        admin_user = User(username="admin_test", hashed_password="hashed_password", role="ADMIN", is_active=True)
        admin_user.roles.append(roles["ADMIN"])
        db.add(admin_user)
        
        erp_user = User(username="erp_test", hashed_password="hashed_password", role="ERP_USER", is_active=True)
        erp_user.roles.append(roles["ERP_USER"])
        db.add(erp_user)
        
        mes_user = User(username="mes_test", hashed_password="hashed_password", role="MES_USER", is_active=True)
        mes_user.roles.append(roles["MES_USER"])
        db.add(mes_user)
        
        wms_user = User(username="wms_test", hashed_password="hashed_password", role="WMS_USER", is_active=True)
        wms_user.roles.append(roles["WMS_USER"])
        db.add(wms_user)
        
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
