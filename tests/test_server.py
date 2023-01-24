"""Core server test."""
from mr_fat_controller.server import app
from fastapi.testclient import TestClient


def test_status() -> None:
    """Test the status request."""
    client = TestClient(app)
    response = client.get('/status')
    assert response.status_code == 200
    assert response.json() == {'ready': True}
