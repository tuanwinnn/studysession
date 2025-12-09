# tests/test_routes.py
from datetime import datetime, timedelta

from app.models import db, StudySession, User


def test_index_route(client):
    """
    Basic sanity check: home page loads.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"<html" in response.data.lower()


def test_protected_sessions_requires_login(client):
    """
    Testing plan 3.b: Protected routes using @login_required.
    /sessions should redirect to login when not logged in.
    """
    response = client.get("/sessions", follow_redirects=False)
    assert response.status_code in (301, 302)
    assert "/auth/login" in response.headers.get("Location", "")


def test_sessions_accessible_when_logged_in(auth_client):
    """
    Testing plan 3.b: /sessions accessible when logged in.
    """
    response = auth_client.get("/sessions")
    # Depending on your template this might be 200 with some HTML.
    assert response.status_code == 200
    assert b"<html" in response.data.lower()


def test_session_create_edit_delete_flow(auth_client, app, user):
    """
    Testing plan 3.c: Session CRUD routes (create, edit, delete).
    Assumes routes:
    - GET/POST /sessions/create
    - GET/POST /sessions/<id>/edit
    - POST /sessions/<id>/delete
    """
    # CREATE
    future_date = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    create_resp = auth_client.post(
        "/sessions/create",
        data={
            "title": "CRUD Session",
            "date": future_date,
            "location": "Room 303",
            "topic": "CRUD Testing",
        },
        follow_redirects=True,
    )
    assert create_resp.status_code == 200

    with app.app_context():
        session = StudySession.query.filter_by(title="CRUD Session").first()
        assert session is not None
        session_id = session.id

    # EDIT
    new_title = "CRUD Session Updated"
    edit_resp = auth_client.post(
        f"/sessions/{session_id}/edit",
        data={
            "title": new_title,
            "date": future_date,
            "location": "Room 303",
            "topic": "Updated Topic",
        },
        follow_redirects=True,
    )
    assert edit_resp.status_code == 200

    with app.app_context():
        updated = StudySession.query.get(session_id)
        assert updated.title == new_title

    # DELETE
    delete_resp = auth_client.post(
        f"/sessions/{session_id}/delete",
        follow_redirects=True,
    )
    assert delete_resp.status_code == 200

    with app.app_context():
        deleted = StudySession.query.get(session_id)
        assert deleted is None


def test_join_and_leave_session(auth_client, app, user, future_session):
    """
    Testing plan 3.d: Join/Leave session logic.
    Assumes routes:
      - POST /sessions/<id>/join
      - POST /sessions/<id>/leave
    and StudySession.members relationship.
    """
    session_id = future_session.id

    # JOIN
    join_resp = auth_client.post(
        f"/sessions/{session_id}/join",
        follow_redirects=True,
    )
    assert join_resp.status_code == 200

    with app.app_context():
        session = StudySession.query.get(session_id)
        assert user in session.members

    # LEAVE
    leave_resp = auth_client.post(
        f"/sessions/{session_id}/leave",
        follow_redirects=True,
    )
    assert leave_resp.status_code == 200

    with app.app_context():
        session = StudySession.query.get(session_id)
        assert user not in session.members
