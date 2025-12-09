# tests/test_forms.py
from datetime import datetime, timedelta

from app.forms import LoginForm, RegistrationForm, SessionForm
from app.models import db, User


def test_login_form_valid_data(app):
    """
    Testing plan 2.b: Login form – valid email + password passes.
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
    Testing plan 2.b: Login form – invalid email fails.
    """
    with app.test_request_context(
        "/auth/login",
        method="POST",
        data={"email": "not-an-email", "password": "secret"},
    ):
        form = LoginForm()
        assert form.validate() is False
        assert form.email.errors


def test_registration_form_email_uniqueness(app):
    """
    Testing plan 2.b: Registration form should reject duplicate email.
    Assumes RegistrationForm has validate_email that checks the DB.
    """
    with app.app_context():
        existing = User(username="exists", email="exists@example.com")
        existing.set_password("pw")
        db.session.add(existing)
        db.session.commit()

    with app.test_request_context(
        "/auth/register",
        method="POST",
        data={
            "username": "newuser",
            "email": "exists@example.com",  # duplicate
            "password": "secret123",
            "confirm_password": "secret123",
        },
    ):
        form = RegistrationForm()
        assert form.validate() is False
        assert form.email.errors


def test_registration_form_password_mismatch(app):
    """
    Testing plan 2.b: Registration form – password rules (matching fields).
    """
    with app.test_request_context(
        "/auth/register",
        method="POST",
        data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "secret123",
            "confirm_password": "different",
        },
    ):
        form = RegistrationForm()
        assert form.validate() is False
        assert form.confirm_password.errors


def test_session_form_required_fields_and_future_date(app):
    """
    Testing plan 2.a: Session creation/edit forms.
    - title, date, location are required
    - date must be in the future (assuming your SessionForm enforces this)
    """

    # valid future date
    future_date = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")

    with app.test_request_context(
        "/sessions/create",
        method="POST",
        data={
            "title": "Study Group",
            "date": future_date,
            "location": "Room 202",
            "topic": "Chapters 5–7",
        },
    ):
        form = SessionForm()
        assert form.validate() is True

    # missing title should fail
    with app.test_request_context(
        "/sessions/create",
        method="POST",
        data={
            "title": "",
            "date": future_date,
            "location": "Room 202",
            "topic": "Chapters 5–7",
        },
    ):
        form = SessionForm()
        assert form.validate() is False
        assert form.title.errors

    # past date should fail (assuming you implement date validation)
    past_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    with app.test_request_context(
        "/sessions/create",
        method="POST",
        data={
            "title": "Old Session",
            "date": past_date,
            "location": "Room 202",
            "topic": "Old stuff",
        },
    ):
        form = SessionForm()
        assert form.validate() is False
        assert form.date.errors
