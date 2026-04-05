def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_get_me_creates_session(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "session_id" in data
    assert data["display_name"] == "Reader"
    assert "reading_session" in response.cookies


def test_get_me_reuses_existing_session(client):
    response1 = client.get("/api/v1/users/me")
    assert response1.status_code == 200
    user1 = response1.json()

    response2 = client.get("/api/v1/users/me")
    assert response2.status_code == 200
    user2 = response2.json()

    assert user1["id"] == user2["id"]


def test_update_display_name(client):
    client.get("/api/v1/users/me")

    response = client.put("/api/v1/users/me", json={"display_name": "BookWorm"})
    assert response.status_code == 200
    assert response.json()["display_name"] == "BookWorm"
