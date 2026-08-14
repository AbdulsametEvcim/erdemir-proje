def test_login_success(client):
    res = client.post("/api/login", json={"username": "testuser", "password": "testpass"})
    assert res.status_code == 200
    assert res.json()["access_token"] == "test-token"


def test_login_wrong_password(client):
    res = client.post("/api/login", json={"username": "testuser", "password": "wrong"})
    assert res.status_code == 401


def test_login_wrong_username(client):
    res = client.post("/api/login", json={"username": "wrong", "password": "testpass"})
    assert res.status_code == 401


def test_protected_endpoint_without_token(client):
    res = client.get("/api/materials")
    assert res.status_code == 401


def test_protected_endpoint_with_wrong_token(client):
    res = client.get("/api/materials", headers={"Authorization": "Bearer wrong-token"})
    assert res.status_code == 401
