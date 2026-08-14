def test_pdf_report_with_turkish_characters_in_name(client, auth_headers):
    create_res = client.post(
        "/api/materials",
        json={"name": "Taşkömürü", "unit": "ton", "current_stock": 50, "critical_threshold": 20},
        headers=auth_headers,
    )
    material_id = create_res.json()["id"]

    res = client.get(f"/api/materials/{material_id}/report", headers=auth_headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")


def test_pdf_report_for_nonexistent_material_returns_404(client, auth_headers):
    res = client.get("/api/materials/999/report", headers=auth_headers)
    assert res.status_code == 404
