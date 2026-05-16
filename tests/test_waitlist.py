from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_join_waitlist():
    response = client.post("/waitlist", json={"email": "test@example.com"})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_duplicate_email():
    client.post("/waitlist", json={"email": "duplicate@example.com"})
    response = client.post("/waitlist", json={"email": "duplicate@example.com"})
    assert response.status_code == 400

def test_get_entry():
    response = client.post("/waitlist", json={"email": "get@example.com"})
    entry_id = response.json()["id"]
    response = client.get(f"/waitlist/{entry_id}")
    assert response.status_code == 200