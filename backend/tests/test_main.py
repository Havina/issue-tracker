from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_read_root():
    response = client.get("/")


    assert response.status_code == 200
    assert response.json() == {
        "message": "Issue Tracker API"
    }

def test_users_me_requires_authentication():
    response = client.get("/users/me")

    assert response.status_code == 401


def test_users_me_rejects_invalid_token():
    response = client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or expired token"
    }


def test_get_issues_requires_authentication():
    response = client.get("/issues")

    assert response.status_code == 401


def test_create_user():
    response = client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpass123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_user_rejects_duplicate_username():
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass123",
    }

    first_response = client.post(
        "./users",
        json=user_data,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "different@example.com",
            "password": "anotherpass123",
        },
    )

    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Username already registered"
    }


def test_create_user_rejects_duplicate_email():
    first_response = client.post(
        "/users",
        json={
            "username": "firstuser",
            "email": "shared@example.com",
            "password": "testpass123",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/users",
        json={
            "username": "seconduser",
            "email": "shared@example.com",
            "password": "anotherpass123",
        },
    )

    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Email already registered"
    }


def test_login_returns_access_token():
    create_response = client.post(
        "/users",
        json={
            "username": "loginuser",
            "email": "loginuser@example.com",
            "password": "testpass123",
        },
    )

    assert create_response.status_code == 201

    login_response = client.post(
        "/login",
        json={
            "username": "loginuser",
            "password": "testpass123",
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
