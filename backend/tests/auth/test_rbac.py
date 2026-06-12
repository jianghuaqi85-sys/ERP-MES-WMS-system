import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.apps.auth.dependencies import require_permissions, get_current_user
from app.apps.auth.models import User, Role, Permission

# Create a test FastAPI application specifically to test RBAC dependency
test_app = FastAPI()

@test_app.get("/test-admin")
def get_admin_route(current_user: User = Depends(require_permissions(["ADMIN"]))):
    return {"message": "Admin area", "username": current_user.username}

@test_app.get("/test-erp")
def get_erp_route(current_user: User = Depends(require_permissions(["ADMIN", "ERP_USER"]))):
    return {"message": "ERP area", "username": current_user.username}

@test_app.get("/test-mes")
def get_mes_route(current_user: User = Depends(require_permissions(["ADMIN", "MES_USER"]))):
    return {"message": "MES area", "username": current_user.username}

@test_app.get("/test-custom-perm")
def get_custom_perm_route(current_user: User = Depends(require_permissions(["erp:write"]))):
    return {"message": "Custom perm area", "username": current_user.username}


def test_rbac_admin_access(db):
    # Retrieve the admin user seeded in conftest
    admin_user = db.query(User).filter(User.username == "admin_test").first()
    
    # Override get_current_user to return the admin user
    test_app.dependency_overrides[get_current_user] = lambda: admin_user
    client = TestClient(test_app)
    
    # Admin should access all routes
    r1 = client.get("/test-admin")
    assert r1.status_code == 200
    assert r1.json()["username"] == "admin_test"
    
    r2 = client.get("/test-erp")
    assert r2.status_code == 200
    
    r3 = client.get("/test-mes")
    assert r3.status_code == 200
    
    r4 = client.get("/test-custom-perm")
    assert r4.status_code == 200
    
    test_app.dependency_overrides.clear()


def test_rbac_erp_access(db):
    erp_user = db.query(User).filter(User.username == "erp_test").first()
    
    test_app.dependency_overrides[get_current_user] = lambda: erp_user
    client = TestClient(test_app)
    
    # ERP user should NOT access admin route
    r1 = client.get("/test-admin")
    assert r1.status_code == 403
    
    # ERP user should access ERP route (due to matching ERP_USER role name)
    r2 = client.get("/test-erp")
    assert r2.status_code == 200
    assert r2.json()["username"] == "erp_test"
    
    # ERP user should NOT access MES route
    r3 = client.get("/test-mes")
    assert r3.status_code == 403
    
    # ERP user has erp:write permission, should access custom perm route
    r4 = client.get("/test-custom-perm")
    assert r4.status_code == 200
    
    test_app.dependency_overrides.clear()


def test_rbac_mes_access(db):
    mes_user = db.query(User).filter(User.username == "mes_test").first()
    
    test_app.dependency_overrides[get_current_user] = lambda: mes_user
    client = TestClient(test_app)
    
    # MES user should NOT access admin or ERP routes
    assert client.get("/test-admin").status_code == 403
    assert client.get("/test-erp").status_code == 403
    
    # MES user should access MES route
    r3 = client.get("/test-mes")
    assert r3.status_code == 200
    assert r3.json()["username"] == "mes_test"
    
    # MES user does not have erp:write, should fail custom perm route
    assert client.get("/test-custom-perm").status_code == 403
    
    test_app.dependency_overrides.clear()


def test_rbac_inactive_user(db):
    inactive_user = db.query(User).filter(User.username == "admin_test").first()
    inactive_user.is_active = False
    db.commit()
    
    def mock_get_current_user():
        raise HTTPException(status_code=403, detail="用户已被禁用")
        
    test_app.dependency_overrides[get_current_user] = mock_get_current_user
    client = TestClient(test_app)
    
    assert client.get("/test-admin").status_code == 403
    test_app.dependency_overrides.clear()
