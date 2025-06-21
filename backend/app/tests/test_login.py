from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_verified_user():
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "secure",
        "is_verified": True
    })
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_login_unverified_user():
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "secure",
        "is_verified": False
    })
    assert response.status_code == 403
    assert response.json()["detail"] == "Email not verified"
