# tests/test_models.py
from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import db, User, StudySession


def test_user_login_behavior_and_get_id(app):
    """
    Testing plan 1.a: User model login behavior.
    - UserMixin should make is_authenticated True
    - get_id should return the primary key as a string
    """
    with app.app_context():
        u = User(username="alice", email="alice@example.com")
        u.set_password("secret123")
        db.session.add(u)
        db.session.commit()

        assert u.is_authenticated
        assert str(u.id) == u.get_id()


def test_user_unique_email_constraint(app):
    """
    Testing plan 1.a: User unique constraints.
    Two users with the same email should violate the unique constraint.
    """
    with app.app_context():
        user1 = User(username="bob", email="bob@example.com")
        user1.set_password("pw1")
        db.session.add(user1)
        db.session.commit()

        user2 = User(username="bobby", email="bob@example.com")
        user2.set_password("pw2")
        db.session.add(user2)

        with pytest.raises(IntegrityError):
            db.session.commit()


def test_studysession_crud_basic(app, user):
    """
    Testing plan 1.b: StudySession CRUD.
    Create, read, update, delete a StudySession.
    """
    with app.app_context():
        # Create
        session = StudySession(
            title="Midterm Review",
            date=datetime.utcnow(),
            location="Room 101",
            topic="Chapters 1–4",
            creator_id=user.id,
        )
        db.session.add(session)
        db.session.commit()
        assert session.id is not None

        # Read
        found = StudySession.query.get(session.id)
        assert found is not None
        assert found.title == "Midterm Review"

        # Update
        found.title = "Updated Midterm Review"
        db.session.commit()
        updated = StudySession.query.get(session.id)
        assert updated.title == "Updated Midterm Review"

        # Delete
        db.session.delete(updated)
        db.session.commit()
        assert StudySession.query.get(session.id) is None


def test_studysession_participants_relationship(app, user):
    """
    Testing plan 1.b: StudySession participants.
    Assumes StudySession.members is a relationship to User.
    """
    with app.app_context():
        # Creator
        creator = user

        # Another participant
        participant = User(username="carol", email="carol@example.com")
        participant.set_password("pw")
        db.session.add(participant)
        db.session.commit()

        session = StudySession(
            title="Group Study",
            date=datetime.utcnow() + timedelta(days=1),
            location="Library",
            topic="Exam 1",
            creator_id=creator.id,
        )
        # assume session.members is a list-like relationship
        session.members.append(participant)
        db.session.add(session)
        db.session.commit()

        saved = StudySession.query.get(session.id)
        assert participant in saved.members
        # and participant should see the session in their joined list if you
        # set a backref such as joined_sessions
        # (this assertion is optional; adjust to your relationship name)
        # assert saved in participant.joined_sessions
