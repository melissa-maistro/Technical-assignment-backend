import pytest
from fastapi.testclient import TestClient
from main import app, users, request_log, MAX_REQUESTS

client = TestClient(app)


# -----------------------------
# Utility: reset in-memory state
# -----------------------------
@pytest.fixture(autouse=True)
def clear_state():
    users.clear()
    request_log.clear()
    yield
    users.clear()
    request_log.clear()


# -----------------------------
# Test: Create user
# -----------------------------
def test_create_user():
    response = client.post("/users/", json={"name": "Melissa"})
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["name"] == "Melissa"


# -----------------------------
# Test: Make valid request
# -----------------------------
def test_make_request_success():
    user_response = client.post("/users/", json={"name": "Test"})
    user_id = user_response.json()["id"]

    response = client.post("/requests/", json={"user_id": user_id})
    assert response.status_code == 201

    data = response.json()
    assert data["id"] == user_id
    assert len(data["requests"]) == 1


# -----------------------------
# Test: 404 if user not found
# -----------------------------
def test_request_user_not_found():
    response = client.post("/requests/", json={"user_id": "invalid"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


# -----------------------------
# Test: Rate limit exceeded
# -----------------------------
def test_rate_limit_exceeded():
    user_response = client.post("/users/", json={"name": "RateLimit"})
    user_id = user_response.json()["id"]

    # make max allowed requests
    for _ in range(MAX_REQUESTS):
        response = client.post("/requests/", json={"user_id": user_id})
        assert response.status_code == 201

    # one extra request should fail
    response = client.post("/requests/", json={"user_id": user_id})
    assert response.status_code == 429
    assert response.json()["detail"] == "Too many requests"


# -----------------------------
# Test: Get quota
# -----------------------------
def test_get_quota():
    user_response = client.post("/users/", json={"name": "QuotaUser"})
    user_id = user_response.json()["id"]

    # make 3 requests
    for _ in range(3):
        client.post("/requests/", json={"user_id": user_id})

    response = client.get(f"/users/{user_id}/quota")
    assert response.status_code == 200

    data = response.json()
    assert data["requests_used"] == 3
    assert data["requests_remaining"] == MAX_REQUESTS - 3
    assert data["limit"] == MAX_REQUESTS