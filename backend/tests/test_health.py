import pytest
from unittest.mock import patch, MagicMock

def test_health_check_success(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "up"
    assert data["redis"] == "up"
    assert "project" in data
    assert "environment" in data

def test_health_check_database_down(client):
    # Mock db.execute to raise an exception
    # Since client fixture overrides get_db, we can mock the session's execute method.
    # But wait, to do that we can patch or mock it.
    # In pytest, we can mock client's dependency or the database connection itself.
    # Let's mock db.execute inside main.py's health_check
    with patch("app.main.Depends") as mock_depends:
        # Instead of patching Depends, we can patch the execute method on the mock DB session
        # Let's write a direct test using the FastAPI test client but mocking database execute.
        # Wait, since the client fixture overrides get_db, the db session is passed to the route.
        # We can mock the session passed to the route.
        pass

    # A simpler way to test the error paths is to mock the sqlalchemy execute or redis ping.
    # Let's write a mock test.
    with patch("sqlalchemy.orm.Session.execute", side_effect=Exception("DB Connection Refused")):
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "down" in data["database"]
        assert data["redis"] == "up"

def test_health_check_redis_down(client):
    with patch("redis.Redis.ping", side_effect=Exception("Redis Connection Timeout")):
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "up"
        assert "down" in data["redis"]
