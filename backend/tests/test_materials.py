def test_create_and_list_material(client, auth_headers):
    res = client.post(
        "/api/materials",
        json={"name": "Test Malzeme", "unit": "ton", "current_stock": 100, "critical_threshold": 20},
        headers=auth_headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "Test Malzeme"
    assert body["status"] == "normal"

    list_res = client.get("/api/materials", headers=auth_headers)
    names = [m["name"] for m in list_res.json()]
    assert "Test Malzeme" in names


def test_create_material_duplicate_name_fails(client, auth_headers):
    payload = {"name": "Dup", "unit": "ton", "current_stock": 10, "critical_threshold": 5}
    client.post("/api/materials", json=payload, headers=auth_headers)
    res = client.post("/api/materials", json=payload, headers=auth_headers)
    assert res.status_code == 400


def test_material_below_threshold_is_critical(client, auth_headers):
    res = client.post(
        "/api/materials",
        json={"name": "Kritik Test", "unit": "ton", "current_stock": 5, "critical_threshold": 10},
        headers=auth_headers,
    )
    assert res.json()["status"] == "kritik"


def test_update_material_threshold(client, auth_headers):
    create_res = client.post(
        "/api/materials",
        json={"name": "Guncellenecek", "unit": "ton", "current_stock": 50, "critical_threshold": 10},
        headers=auth_headers,
    )
    material_id = create_res.json()["id"]

    res = client.put(
        f"/api/materials/{material_id}",
        json={"critical_threshold": 60},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "kritik"


def test_update_material_duplicate_name_fails(client, auth_headers):
    client.post(
        "/api/materials",
        json={"name": "Isim A", "unit": "ton", "current_stock": 10, "critical_threshold": 5},
        headers=auth_headers,
    )
    create_res = client.post(
        "/api/materials",
        json={"name": "Isim B", "unit": "ton", "current_stock": 10, "critical_threshold": 5},
        headers=auth_headers,
    )
    material_id = create_res.json()["id"]

    res = client.put(f"/api/materials/{material_id}", json={"name": "Isim A"}, headers=auth_headers)
    assert res.status_code == 400


def test_delete_material(client, auth_headers):
    create_res = client.post(
        "/api/materials",
        json={"name": "Silinecek", "unit": "ton", "current_stock": 1, "critical_threshold": 1},
        headers=auth_headers,
    )
    material_id = create_res.json()["id"]

    res = client.delete(f"/api/materials/{material_id}", headers=auth_headers)
    assert res.status_code == 200

    list_res = client.get("/api/materials", headers=auth_headers)
    ids = [m["id"] for m in list_res.json()]
    assert material_id not in ids


def test_delete_nonexistent_material_returns_404(client, auth_headers):
    res = client.delete("/api/materials/999", headers=auth_headers)
    assert res.status_code == 404


def test_search_materials(client, auth_headers):
    client.post(
        "/api/materials",
        json={"name": "Aranan Malzeme", "unit": "ton", "current_stock": 10, "critical_threshold": 5},
        headers=auth_headers,
    )
    client.post(
        "/api/materials",
        json={"name": "Baska Bir Sey", "unit": "ton", "current_stock": 10, "critical_threshold": 5},
        headers=auth_headers,
    )

    res = client.get("/api/materials", params={"search": "Aranan"}, headers=auth_headers)
    names = [m["name"] for m in res.json()]
    assert names == ["Aranan Malzeme"]
