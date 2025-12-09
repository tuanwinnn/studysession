# tests/test_models.py
from datetime import datetime

from app.models import db, User, StudySession


def test_create_user(app):
    """
    Make sure a User can be created and saved to the database.
    """
    with app.app_context():
        user = User(
            username="alice",
            email="alice@example.com",
            password_hash="fake-hash",
        )
        db.session.add(user)
        db.session.commit()

        assert user.id is not None  # got a primary key

        found = User.query.filter_by(email="alice@example.com").first()
        assert found is not None
        assert found.username == "alice"


def test_create_study_session(app):
    """
    Make sure a StudySession can be created and linked to a User.
    """
    with app.app_context():
        user = User(
            username="bob",
            email="bob@example.com",
            password_hash="fake-hash",
        )
        db.session.add(user)
        db.session.commit()

        session = StudySession(
            title="Midterm Review",
            date=datetime.utcnow(),
            location="Library 101",
            topic="Chapters 1–3",
            creator_id=user.id,
        )
        db.session.add(session)
        db.session.commit()

        assert session.id is not None
        assert session.creator_id == user.id
