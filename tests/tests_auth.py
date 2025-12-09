# tests/test_auth.py
from app.models import db, User


def test_login_page_get(client):
    """
    Testing plan 3.a: /auth/login should render the login form.
    """
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Email" in response.data
    assert b"Password" in response.data


def test_register_page_get(client):
    """
    Testing plan 3.a: /auth/register should render the registration form.
    """
    response = client.get("/auth/register")
    assert response.status_code == 200
    assert b"Register" in response.data  # assumes template has this word


def test_register_creates_user(client, app):
    """
    Testing plan 3.a: POST /auth/register should create a new user in the DB.
    """
    response = client.post(
        "/auth/register",
        data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "secret123",
            "confirm_password": "secret123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email="new@example.com").first()
        assert user is not None
        # optionally, check password_hash is not plain text
        assert user.password_hash != "secret123"


def test_login_with_correct_credentials(client, app):
    """
    Testing plan 3.a: /auth/login logs in a valid user.
    """
    with app.app_context():
        user = User(username="loginuser", email="login@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/auth/login",
        data={"email": "login@example.com", "password": "password123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    # After login we expect to be redirected away from login page
    assert b"Login" not in response.data or b"Email" not in response.data


def test_logout_clears_session(auth_client):
    """
    Testing plan 3.a: /auth/logout should log the user out.
    """
    # logout
    response = auth_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200

    # After logout, trying to access a protected route should redirect to login
    response2 = auth_client.get("/sessions", follow_redirects=False)
    assert response2.status_code in (301, 302)
    assert "/auth/login" in response2.headers.get("Location", "")
