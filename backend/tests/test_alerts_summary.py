def test_alerts_returns_only_critical(client, auth_headers):
    client.post(
        "/api/materials",
        json={"name": "Normal Malzeme", "unit": "ton", "current_stock": 100, "critical_threshold": 10},
        headers=auth_headers,
    )
    client.post(
        "/api/materials",
        json={"name": "Kritik Malzeme", "unit": "ton", "current_stock": 5, "critical_threshold": 10},
        headers=auth_headers,
    )

    res = client.get("/api/alerts", headers=auth_headers)
    names = [a["name"] for a in res.json()]
    assert "Kritik Malzeme" in names
    assert "Normal Malzeme" not in names


def test_summary_counts(client, auth_headers):
    client.post(
        "/api/materials",
        json={"name": "A", "unit": "ton", "current_stock": 100, "critical_threshold": 10},
        headers=auth_headers,
    )
    client.post(
        "/api/materials",
        json={"name": "B", "unit": "ton", "current_stock": 5, "critical_threshold": 10},
        headers=auth_headers,
    )

    res = client.get("/api/summary", headers=auth_headers)
    body = res.json()
    assert body["total_materials"] == 2
    assert body["critical_materials"] == 1


def test_summary_consumption_7d_reflects_movement(client, auth_headers):
    create_res = client.post(
        "/api/materials",
        json={"name": "Tuketim Malzemesi", "unit": "ton", "current_stock": 100, "critical_threshold": 10},
        headers=auth_headers,
    )
    material_id = create_res.json()["id"]
    client.post(
        "/api/movements",
        json={"material_id": material_id, "movement_type": "cikis", "quantity": 25},
        headers=auth_headers,
    )

    res = client.get("/api/summary", headers=auth_headers)
    assert res.json()["total_consumption_7d"] == 25


def test_summary_consumption_7d_ignores_non_ton_units(client, auth_headers):
    ton_res = client.post(
        "/api/materials",
        json={"name": "Ton Malzeme", "unit": "ton", "current_stock": 100, "critical_threshold": 10},
        headers=auth_headers,
    )
    m3_res = client.post(
        "/api/materials",
        json={"name": "M3 Malzeme", "unit": "m³", "current_stock": 5000, "critical_threshold": 500},
        headers=auth_headers,
    )
    client.post(
        "/api/movements",
        json={"material_id": ton_res.json()["id"], "movement_type": "cikis", "quantity": 10},
        headers=auth_headers,
    )
    client.post(
        "/api/movements",
        json={"material_id": m3_res.json()["id"], "movement_type": "cikis", "quantity": 4000},
        headers=auth_headers,
    )

    res = client.get("/api/summary", headers=auth_headers)
    assert res.json()["total_consumption_7d"] == 10


def test_consumption_comparison_excludes_non_ton_units(client, auth_headers):
    ton_res = client.post(
        "/api/materials",
        json={"name": "Ton Karsilastirma", "unit": "ton", "current_stock": 100, "critical_threshold": 10},
        headers=auth_headers,
    )
    m3_res = client.post(
        "/api/materials",
        json={"name": "M3 Karsilastirma", "unit": "m³", "current_stock": 5000, "critical_threshold": 500},
        headers=auth_headers,
    )
    client.post(
        "/api/movements",
        json={"material_id": ton_res.json()["id"], "movement_type": "cikis", "quantity": 10},
        headers=auth_headers,
    )
    client.post(
        "/api/movements",
        json={"material_id": m3_res.json()["id"], "movement_type": "cikis", "quantity": 4000},
        headers=auth_headers,
    )

    res = client.get("/api/reports/consumption-comparison", params={"days": 30}, headers=auth_headers)
    names = [item["material_name"] for item in res.json()]
    assert "Ton Karsilastirma" in names
    assert "M3 Karsilastirma" not in names
