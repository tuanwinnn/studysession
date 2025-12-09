# tests/conftest.py
import os
import pytest

from app import create_app
from app.models import db as _db


@pytest.fixture
def app(tmp_path):
    """
    Create a new app instance for each test, with:
    - TESTING mode on
    - CSRF disabled (makes form testing easier)
    - SQLite test database in a temp folder
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
    """
    Flask test client for making requests to routes.
    """
    return app.test_client()
