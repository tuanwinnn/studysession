import pytest
from flask import url_for
from datetime import datetime, timedelta

from app.models import db, User, StudySession
def login(client, email, password):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )

def test_view_sessions_requires_login(client):
    response = client.get("/sessions", follow_redirects=False)
    assert response.status_code in (301, 302)
    assert "/auth/login" in response.headers.get("Location", "")

def test_create_session_logged_in(client, user, app):
    login(client, user.email, "password123")

    response = client.post(
        "/sessions/create",
        data={
            "title": "Test Session",
            "date": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            "location": "Library",
            "topic": "Testing",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Verify that the session was actually created in the DB
    with app.app_context():
        created = StudySession.query.filter_by(title="Test Session").first()
        assert created is not None


def test_join_and_leave_session(client, user, app, future_session):
    login(client, user.email, "password123")

    session_id = future_session.id

    # JOIN
    join_response = client.post(
        f"/sessions/{session_id}/join",
        follow_redirects=True,
    )
    assert join_response.status_code == 200

    with app.app_context():
        session = StudySession.query.get(session_id)
        assert session is not None
        assert user in session.members

    # LEAVE
    leave_response = client.post(
        f"/sessions/{session_id}/leave",
        follow_redirects=True,
    )
    assert leave_response.status_code == 200

    with app.app_context():
        session = StudySession.query.get(session_id)
        assert user not in session.members


def test_student_cannot_access_admin_routes(client, user):
    login(client, user.email, "password123")

    response = client.get("/admin/dashboard", follow_redirects=False)
    # Depending on your implementation, you might:
    # - return 403, or
    # - redirect to login.
    assert response.status_code in (301, 302, 403)

def test_invalid_session_redirects(client, user):
    login(client, user.email, "password123")

    response = client.get("/sessions/9999", follow_redirects=False)
    # If you used get_or_404 you'll get a 404 directly.
    # If you chose to redirect somewhere else, you'll see 302.
    assert response.status_code in (404, 302)
