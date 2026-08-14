def test_environmental_summary_computes_co2(client, auth_headers):
    create_res = client.post(
        "/api/materials",
        json={"name": "Kok Kömürü", "unit": "ton", "current_stock": 100, "critical_threshold": 10, "co2_factor": 3000},
        headers=auth_headers,
    )
    material_id = create_res.json()["id"]
    client.post(
        "/api/movements",
        json={"material_id": material_id, "movement_type": "cikis", "quantity": 10},
        headers=auth_headers,
    )

    res = client.get("/api/environmental/summary", params={"days": 30}, headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    item = next(i for i in body["items"] if i["material_id"] == material_id)
    assert item["total_co2_kg"] == 30000
    assert body["total_co2_kg"] >= 30000


def test_environmental_summary_zero_factor_material(client, auth_headers):
    create_res = client.post(
        "/api/materials",
        json={"name": "Yedek Parça", "unit": "adet", "current_stock": 10, "critical_threshold": 2},
        headers=auth_headers,
    )
    material_id = create_res.json()["id"]
    client.post(
        "/api/movements",
        json={"material_id": material_id, "movement_type": "cikis", "quantity": 5},
        headers=auth_headers,
    )

    res = client.get("/api/environmental/summary", headers=auth_headers)
    item = next(i for i in res.json()["items"] if i["material_id"] == material_id)
    assert item["total_co2_kg"] == 0


def test_summary_pdf_report(client, auth_headers):
    client.post(
        "/api/materials",
        json={"name": "Rapor Malzemesi", "unit": "ton", "current_stock": 10, "critical_threshold": 20},
        headers=auth_headers,
    )
    res = client.get("/api/reports/summary-pdf", headers=auth_headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")
