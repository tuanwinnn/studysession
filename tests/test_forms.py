# tests/test_forms.py
from app.forms import LoginForm


def test_login_form_valid_data(app):
    """
    Valid email + non-empty password => form should validate.
    """
    with app.test_request_context(
        "/auth/login",
        method="POST",
        data={"email": "test@example.com", "password": "secret"},
    ):
        form = LoginForm()
        assert form.validate() is True


def test_login_form_invalid_email(app):
    """
    Invalid email string => form should NOT validate.
    """
    with app.test_request_context(
        "/auth/login",
        method="POST",
        data={"email": "not-an-email", "password": "secret"},
    ):
        form = LoginForm()
        assert form.validate() is False
        assert form.email.errors  # there should be at least one error


def test_login_form_missing_password(app):
    """
    Missing password => form should NOT validate.
    """
    with app.test_request_context(
        "/auth/login",
        method="POST",
        data={"email": "test@example.com", "password": ""},
    ):
        form = LoginForm()
        assert form.validate() is False
        assert form.password.errors
