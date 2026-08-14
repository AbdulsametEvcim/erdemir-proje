def create_material(client, auth_headers, **overrides):
    payload = {"name": "Hareket Malzemesi", "unit": "ton", "current_stock": 100, "critical_threshold": 20}
    payload.update(overrides)
    res = client.post("/api/materials", json=payload, headers=auth_headers)
    return res.json()


def test_giris_movement_stores_supplier(client, auth_headers):
    material = create_material(client, auth_headers, name="Tedarikci Malzemesi")
    res = client.post(
        "/api/movements",
        json={
            "material_id": material["id"],
            "movement_type": "giris",
            "quantity": 10,
            "supplier": "ABC Madencilik",
        },
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["supplier"] == "ABC Madencilik"


def test_cikis_movement_ignores_supplier(client, auth_headers):
    material = create_material(client, auth_headers, name="Cikis Tedarikci")
    res = client.post(
        "/api/movements",
        json={
            "material_id": material["id"],
            "movement_type": "cikis",
            "quantity": 5,
            "supplier": "Yanlislikla Girildi",
        },
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["supplier"] is None


def test_cikis_movement_reduces_stock(client, auth_headers):
    material = create_material(client, auth_headers)
    res = client.post(
        "/api/movements",
        json={"material_id": material["id"], "movement_type": "cikis", "quantity": 30},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["quantity"] == 30

    mat_res = client.get("/api/materials", headers=auth_headers)
    updated = next(m for m in mat_res.json() if m["id"] == material["id"])
    assert updated["current_stock"] == 70


def test_giris_movement_increases_stock(client, auth_headers):
    material = create_material(client, auth_headers, name="Giris Malzemesi")
    client.post(
        "/api/movements",
        json={"material_id": material["id"], "movement_type": "giris", "quantity": 15},
        headers=auth_headers,
    )

    mat_res = client.get("/api/materials", headers=auth_headers)
    updated = next(m for m in mat_res.json() if m["id"] == material["id"])
    assert updated["current_stock"] == 115


def test_cikis_more_than_stock_fails(client, auth_headers):
    material = create_material(client, auth_headers, name="Az Stok", current_stock=10)
    res = client.post(
        "/api/movements",
        json={"material_id": material["id"], "movement_type": "cikis", "quantity": 50},
        headers=auth_headers,
    )
    assert res.status_code == 400


def test_invalid_movement_type_fails(client, auth_headers):
    material = create_material(client, auth_headers, name="Gecersiz Tip")
    res = client.post(
        "/api/movements",
        json={"material_id": material["id"], "movement_type": "yanlis", "quantity": 5},
        headers=auth_headers,
    )
    assert res.status_code == 400


def test_negative_quantity_fails(client, auth_headers):
    material = create_material(client, auth_headers, name="Negatif")
    res = client.post(
        "/api/movements",
        json={"material_id": material["id"], "movement_type": "cikis", "quantity": -5},
        headers=auth_headers,
    )
    assert res.status_code == 400


def test_movement_for_nonexistent_material_fails(client, auth_headers):
    res = client.post(
        "/api/movements",
        json={"material_id": 999, "movement_type": "cikis", "quantity": 5},
        headers=auth_headers,
    )
    assert res.status_code == 404


def test_movements_filter_by_material(client, auth_headers):
    m1 = create_material(client, auth_headers, name="Filtre A")
    m2 = create_material(client, auth_headers, name="Filtre B")
    client.post(
        "/api/movements",
        json={"material_id": m1["id"], "movement_type": "cikis", "quantity": 5},
        headers=auth_headers,
    )
    client.post(
        "/api/movements",
        json={"material_id": m2["id"], "movement_type": "cikis", "quantity": 5},
        headers=auth_headers,
    )

    res = client.get("/api/movements", params={"material_id": m1["id"]}, headers=auth_headers)
    body = res.json()
    assert len(body) == 1
    assert body[0]["material_id"] == m1["id"]


def test_movements_filter_by_type(client, auth_headers):
    material = create_material(client, auth_headers, name="Tip Filtre")
    client.post(
        "/api/movements",
        json={"material_id": material["id"], "movement_type": "giris", "quantity": 5},
        headers=auth_headers,
    )
    client.post(
        "/api/movements",
        json={"material_id": material["id"], "movement_type": "cikis", "quantity": 2},
        headers=auth_headers,
    )

    res = client.get(
        "/api/movements",
        params={"material_id": material["id"], "movement_type": "giris"},
        headers=auth_headers,
    )
    body = res.json()
    assert len(body) == 1
    assert body[0]["movement_type"] == "giris"
