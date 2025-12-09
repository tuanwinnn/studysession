# tests/test_routes.py


def test_index_route(client):
    """
    GET / should return 200 and some HTML.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"<html" in response.data.lower()


def test_feature_route(client):
    """
    GET /feature should return 200 and some HTML.
    """
    response = client.get("/feature")
    assert response.status_code == 200
    assert b"<html" in response.data.lower()
