"""Core API tests."""
from mr_fat_controller.server import app
from fastapi.testclient import TestClient


def test_status(empty_database: None) -> None:
    """Test the status request."""
    client = TestClient(app)
    response = client.get('/api/status')
    assert response.status_code == 200
    assert response.json() == {'ready': True}
