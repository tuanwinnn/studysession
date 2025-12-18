# tests/conftest.py
import os
from datetime import datetime, timedelta

import pytest

from app import create_app
from app.models import db as _db, User, StudySession


@pytest.fixture
def app(tmp_path):
    """
    Create a new app instance for each test with:
    - TESTING mode on
    - CSRF disabled (so form tests are simple)
    - SQLite test DB in a temp folder
    """
    test_db_path = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"

    app = create_app()
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client to call routes."""
    return app.test_client()


@pytest.fixture
def user(app):
    """
    A single test user in the DB.
    Assumes User has set_password().
    """
    u = User(username="testuser", email="test@example.com")
    u.set_password("password123")
    _db.session.add(u)
    _db.session.commit()
    return u


@pytest.fixture
def auth_client(client, user):
    """
    Test client that is already logged in as `user`.
    Uses /auth/login route.
    """
    response = client.post(
        "/auth/login",
        data={"email": user.email, "password": "password123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    return client


@pytest.fixture
def future_session(app, user):
    """
    A StudySession in the future owned by `user`.
    Useful for join/leave and CRUD tests.
    Assumes StudySession has a members relationship.
    """
    session = StudySession(
        title="Future Study Session",
        date=datetime.utcnow() + timedelta(days=1),
        location="Library 101",
        topic="Chapters 1–3",
        creator_id=user.id,
    )
    _db.session.add(session)
    _db.session.commit()
    return session
