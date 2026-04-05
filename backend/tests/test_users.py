TEST_EMAIL = "test@example.com"
TEST_DISPLAY = "Tester"


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_register_creates_user(client):
    response = client.post(
        "/api/v1/users/register",
        json={"email": TEST_EMAIL, "display_name": TEST_DISPLAY},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == TEST_EMAIL
    assert data["display_name"] == TEST_DISPLAY
    assert "id" in data
    assert "session_id" in data  # UserAuthResponse includes session_id


def test_register_duplicate_email_returns_409(client):
    client.post("/api/v1/users/register", json={"email": TEST_EMAIL})
    response = client.post("/api/v1/users/register", json={"email": TEST_EMAIL})
    assert response.status_code == 409


def test_login_returns_session(client):
    client.post("/api/v1/users/register", json={"email": TEST_EMAIL})
    response = client.post("/api/v1/users/login", json={"email": TEST_EMAIL})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == TEST_EMAIL
    assert "session_id" in data


def test_login_unknown_email_returns_404(client):
    response = client.post("/api/v1/users/login", json={"email": "nobody@example.com"})
    assert response.status_code == 404


def test_get_me_requires_auth(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_get_me_with_session(client):
    reg = client.post(
        "/api/v1/users/register",
        json={"email": TEST_EMAIL, "display_name": TEST_DISPLAY},
    )
    session_id = reg.json()["session_id"]

    response = client.get(
        "/api/v1/users/me",
        cookies={"reading_session": session_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == TEST_EMAIL
    # session_id is NOT included in the public UserResponse
    assert "session_id" not in data


def test_update_display_name(client):
    reg = client.post("/api/v1/users/register", json={"email": TEST_EMAIL})
    session_id = reg.json()["session_id"]

    response = client.put(
        "/api/v1/users/me",
        json={"display_name": "BookWorm"},
        cookies={"reading_session": session_id},
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "BookWorm"


def test_logout_invalidates_session(client):
    reg = client.post("/api/v1/users/register", json={"email": TEST_EMAIL})
    session_id = reg.json()["session_id"]

    client.post("/api/v1/users/logout", cookies={"reading_session": session_id})

    # Session is now NULL — /me should 401
    response = client.get("/api/v1/users/me", cookies={"reading_session": session_id})
    assert response.status_code == 401

