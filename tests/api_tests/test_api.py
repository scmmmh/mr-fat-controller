"""Core API tests."""
from fastapi.testclient import TestClient

from mr_fat_controller.server import app


def test_status(empty_database: None) -> None:  # noqa: ARG001
    """Test the status request."""
    client = TestClient(app)
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json() == {"ready": True}
