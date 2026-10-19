def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_routes_registered(client):
    paths = {route.path for route in client.app.routes}
    assert "/health" in paths
    assert "/api/v1/meetings/" in paths or any(p.startswith("/api/v1/meetings") for p in paths)
    assert any("/api/v1/transcripts" in p for p in paths)
    assert any("/api/v1/summary" in p for p in paths)
    assert any("ws/meetings" in p for p in paths)


def test_create_and_get_meeting(client):
    created = client.post("/api/v1/meetings/", json={"title": "Standup"})
    assert created.status_code == 200
    body = created.json()
    assert body["title"] == "Standup"
    assert body["id"]

    fetched = client.get(f"/api/v1/meetings/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == body["id"]
