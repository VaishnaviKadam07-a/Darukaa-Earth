from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_requires_valid_email():
    response = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "secret123"},
    )
    assert response.status_code == 422


def test_login_unknown_user_returns_401():
    response = client.post(
        "/api/auth/login",
        data={"username": "nobody@example.com", "password": "whatever"},
    )
    assert response.status_code == 401
