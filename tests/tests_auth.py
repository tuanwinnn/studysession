# tests/test_auth.py


def test_login_page_get(client):
    """
    GET /auth/login should return the login form.
    """
    response = client.get("/auth/login")
    assert response.status_code == 200
    # Check that the form fields appear in the HTML
    assert b"Email" in response.data
    assert b"Password" in response.data


def test_login_page_post_invalid_data(client):
    """
    POST /auth/login with bad data should stay on the login page (no crash).
    """
    response = client.post(
        "/auth/login",
        data={"email": "not-an-email", "password": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    # We expect to still be on a page that looks like the login form
    assert b"Email" in response.data
    assert b"Password" in response.data
