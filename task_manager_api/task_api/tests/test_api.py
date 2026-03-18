"""
Tests for Task Manager API
Run: pytest tests/ -v --cov=. --cov-report=term-missing
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# Use SQLite for tests (no PostgreSQL needed)
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def registered_user(client):
    client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    })
    return {"username": "testuser", "password": "testpass123"}

@pytest.fixture
def auth_headers(client, registered_user):
    response = client.post("/auth/login", data=registered_user)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# ── Health ──────────────────────────────────────────
class TestHealth:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200

# ── Auth ──────────────────────────────────────────
class TestAuth:
    def test_register_success(self, client):
        r = client.post("/auth/register", json={
            "email": "new@example.com", "username": "newuser", "password": "pass123"
        })
        assert r.status_code == 201
        assert r.json()["email"] == "new@example.com"
        assert "hashed_password" not in r.json()

    def test_register_duplicate_email(self, client, registered_user):
        r = client.post("/auth/register", json={
            "email": "test@example.com", "username": "other", "password": "pass"
        })
        assert r.status_code == 400
        assert "Email already registered" in r.json()["detail"]

    def test_register_duplicate_username(self, client, registered_user):
        r = client.post("/auth/register", json={
            "email": "other@example.com", "username": "testuser", "password": "pass"
        })
        assert r.status_code == 400

    def test_login_success(self, client, registered_user):
        r = client.post("/auth/login", data=registered_user)
        assert r.status_code == 200
        assert "access_token" in r.json()
        assert "refresh_token" in r.json()

    def test_login_wrong_password(self, client, registered_user):
        r = client.post("/auth/login", data={"username": "testuser", "password": "wrong"})
        assert r.status_code == 401

    def test_login_nonexistent_user(self, client):
        r = client.post("/auth/login", data={"username": "ghost", "password": "pass"})
        assert r.status_code == 401

# ── Tasks ──────────────────────────────────────────
class TestTasks:
    def test_create_task(self, client, auth_headers):
        r = client.post("/tasks/", json={"title": "Buy groceries"}, headers=auth_headers)
        assert r.status_code == 201
        assert r.json()["title"] == "Buy groceries"
        assert r.json()["status"] == "todo"

    def test_create_task_unauthorized(self, client):
        r = client.post("/tasks/", json={"title": "Test"})
        assert r.status_code == 401

    def test_list_tasks_empty(self, client, auth_headers):
        r = client.get("/tasks/", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["total"] == 0
        assert r.json()["items"] == []

    def test_list_tasks_with_data(self, client, auth_headers):
        client.post("/tasks/", json={"title": "Task 1"}, headers=auth_headers)
        client.post("/tasks/", json={"title": "Task 2"}, headers=auth_headers)
        r = client.get("/tasks/", headers=auth_headers)
        assert r.json()["total"] == 2

    def test_list_tasks_pagination(self, client, auth_headers):
        for i in range(5):
            client.post("/tasks/", json={"title": f"Task {i}"}, headers=auth_headers)
        r = client.get("/tasks/?page=1&page_size=2", headers=auth_headers)
        assert len(r.json()["items"]) == 2
        assert r.json()["total"] == 5

    def test_list_tasks_filter_by_status(self, client, auth_headers):
        client.post("/tasks/", json={"title": "Todo task", "status": "todo"}, headers=auth_headers)
        client.post("/tasks/", json={"title": "Done task", "status": "done"}, headers=auth_headers)
        r = client.get("/tasks/?status=done", headers=auth_headers)
        assert r.json()["total"] == 1
        assert r.json()["items"][0]["title"] == "Done task"

    def test_get_task(self, client, auth_headers):
        created = client.post("/tasks/", json={"title": "My task"}, headers=auth_headers).json()
        r = client.get(f"/tasks/{created['id']}", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["title"] == "My task"

    def test_get_task_not_found(self, client, auth_headers):
        r = client.get("/tasks/9999", headers=auth_headers)
        assert r.status_code == 404

    def test_update_task(self, client, auth_headers):
        created = client.post("/tasks/", json={"title": "Old title"}, headers=auth_headers).json()
        r = client.patch(f"/tasks/{created['id']}", json={"title": "New title", "status": "done"}, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["title"] == "New title"
        assert r.json()["status"] == "done"

    def test_soft_delete_task(self, client, auth_headers):
        created = client.post("/tasks/", json={"title": "Delete me"}, headers=auth_headers).json()
        r = client.delete(f"/tasks/{created['id']}", headers=auth_headers)
        assert r.status_code == 204
        # Task should not appear in list
        r2 = client.get("/tasks/", headers=auth_headers)
        assert r2.json()["total"] == 0

    def test_cannot_access_other_users_task(self, client, auth_headers):
        # Create second user
        client.post("/auth/register", json={"email": "user2@ex.com", "username": "user2", "password": "pass"})
        login2 = client.post("/auth/login", data={"username": "user2", "password": "pass"}).json()
        headers2 = {"Authorization": f"Bearer {login2['access_token']}"}

        # user2 creates task
        task = client.post("/tasks/", json={"title": "Private task"}, headers=headers2).json()

        # user1 tries to access it
        r = client.get(f"/tasks/{task['id']}", headers=auth_headers)
        assert r.status_code == 404
