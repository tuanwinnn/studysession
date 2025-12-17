import pytest
from flask import url_for
from datetime import datetime, timedelta

from app.models import db, User, StudySession
def login(client, username, password):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )

def test_view_sessions_requires_login(client):
    response = client.get("/sessions", follow_redirects=False)
    assert response.status_code == 403 or b"Unauthorized" in response.data # UNAUTHORIZED ERROR CODE
    assert b"/auth/login" in response.data

def test_create_session_logged_in(client, test_user):
    login(client, test_user.username, "password123")

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
    assert b"Test Session created successfully" in response.data

def test_join_and_leave_session(client, test_user, test_session):
    login(client, test_user.username, "password123")

    join_response = client.post(
        f"/sessions/{test_session.id}/join",
        follow_redirects=True,
    )
    assert join_response.status_code == 200
    assert b"Joined session successfully" in join_response.data

    leave_response = client.post(
        f"/sessions/{test_session.id}/leave",
        follow_redirects=True,
    )
    assert leave_response.status_code == 200
    assert b"Left session successfully" in leave_response.data

def test_student_cannot_access_admin_routes(client, test_user):
    login(client, test_user.username, "password123")

    response = client.get("/admin/dashboard", follow_redirects=False)
    assert response.status_code == 403 or b"Unauthorized" in response.data # UNAUTHORIZED ERROR CODE

def test_invalid_session_redirects(client, test_user):
    login(client, test_user.username, "password123")

    response = client.get("/sessions/9999", follow_redirects=True)
    assert response.status_code == 404 # NOT FOUND ERROR CODE
    assert b"Session not found" in response.data