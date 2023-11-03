"""Core API tests."""
from fastapi.testclient import TestClient

from mr_fat_controller.server import app


def test_empty_controllers(empty_database: None) -> None:  # noqa: ARG001
    """Test an initial empty controllers list."""
    client = TestClient(app)
    response = client.get("/api/controllers")
    assert response.status_code == 200
    assert response.json() == []


def test_create_controller(empty_database: None) -> None:  # noqa: ARG001
    """Test that creating a controller persists to the database."""
    client = TestClient(app)
    response = client.post("/api/controllers", json={"id": "1", "baseurl": "http://controller.example.com"})
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "baseurl": "http://controller.example.com",
        "name": "New controller",
        "status": "unknown",
    }
    response = client.get("/api/controllers")
    assert response.status_code == 200
    assert response.json() == [
        {"id": "1", "baseurl": "http://controller.example.com", "name": "New controller", "status": "unknown"}
    ]


def test_fail_create_duplicate_controller(empty_database: None) -> None:  # noqa: ARG001
    """Test that creating a duplicate controller fails."""
    client = TestClient(app)
    response = client.post("/api/controllers", json={"id": "1", "baseurl": "http://controller1.example.com"})
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "baseurl": "http://controller1.example.com",
        "name": "New controller",
        "status": "unknown",
    }
    response = client.post("/api/controllers", json={"id": "1", "baseurl": "http://controller2.example.com"})
    assert response.status_code == 409


def test_fail_create_invalid_controller(empty_database: None) -> None:  # noqa: ARG001
    """Test that creating an invalid controller fails."""
    client = TestClient(app)
    response = client.post("/api/controllers", json={})
    assert response.status_code == 422
    response = client.post("/api/controllers", json={"id": "1"})
    assert response.status_code == 422
    response = client.post("/api/controllers", json={"baseurl": "http://controller.example.com"})
    assert response.status_code == 422
    response = client.post("/api/controllers", json={"id": "", "baseurl": ""})
    assert response.status_code == 422
    response = client.post("/api/controllers", json={"id": "", "baseurl": "http://controller.example.com"})
    assert response.status_code == 422
    response = client.post("/api/controllers", json={"id": "1", "baseurl": "bla"})
    assert response.status_code == 422
    response = client.post("/api/controllers", json={"id": "1", "baseurl": "bla://example.com"})
    assert response.status_code == 422


def test_fail_get_missing_controller(empty_database: None) -> None:  # noqa: ARG001
    """Test that getting a non-existant controller fails."""
    client = TestClient(app)
    response = client.get("/api/controllers/does-not-exist")
    assert response.status_code == 404


def test_update_controller_name(empty_database: None) -> None:  # noqa: ARG001
    """Test that updating a controller name persists to the database."""
    client = TestClient(app)
    response = client.post("/api/controllers", json={"id": "1", "baseurl": "http://controller.example.com"})
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "baseurl": "http://controller.example.com",
        "name": "New controller",
        "status": "unknown",
    }
    new_controller_id = response.json()["id"]
    response = client.put(f"/api/controllers/{new_controller_id}", json={"name": "Controller 1"})
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "baseurl": "http://controller.example.com",
        "name": "Controller 1",
        "status": "unknown",
    }
    response = client.get(f"/api/controllers/{new_controller_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "baseurl": "http://controller.example.com",
        "name": "Controller 1",
        "status": "unknown",
    }


def test_update_controller_baseurl(empty_database: None) -> None:  # noqa: ARG001
    """Test that updating a controller baseurl persists to the database."""
    client = TestClient(app)
    response = client.post("/api/controllers", json={"id": "1", "baseurl": "http://controller.example.com"})
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "baseurl": "http://controller.example.com",
        "name": "New controller",
        "status": "unknown",
    }
    new_controller_id = response.json()["id"]
    response = client.put(f"/api/controllers/{new_controller_id}", json={"baseurl": "http://controller1.example.com"})
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "baseurl": "http://controller1.example.com",
        "name": "New controller",
        "status": "unknown",
    }
    response = client.get(f"/api/controllers/{new_controller_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "baseurl": "http://controller1.example.com",
        "name": "New controller",
        "status": "unknown",
    }


def test_fail_update_missing_controller(empty_database: None) -> None:  # noqa: ARG001
    """Test that updating a non-existant controller fails."""
    client = TestClient(app)
    response = client.put("/api/controllers/does-not-exist", json={"name": "Controller 1"})
    assert response.status_code == 404


def test_fail_update_invalid_controller(empty_database: None) -> None:  # noqa: ARG001
    """Test that updating a controller with invalid data fails."""
    client = TestClient(app)
    response = client.post("/api/controllers", json={"id": "1", "baseurl": "http://controller1.example.com"})
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "baseurl": "http://controller1.example.com",
        "name": "New controller",
        "status": "unknown",
    }
    new_controller_id = response.json()["id"]
    response = client.put(f"/api/controllers/{new_controller_id}", json={"baseurl": ""})
    assert response.status_code == 422
    response = client.put(f"/api/controllers/{new_controller_id}", json={"baseurl": "bla"})
    assert response.status_code == 422
    response = client.put(f"/api/controllers/{new_controller_id}", json={"baseurl": "bla://example.com"})
    assert response.status_code == 422
    response = client.put(f"/api/controllers/{new_controller_id}", json={"name": ""})
    assert response.status_code == 422


def test_delete_controller(empty_database: None) -> None:  # noqa: ARG001
    """Test that deleting a controller works."""
    client = TestClient(app)
    response = client.post("/api/controllers", json={"id": "1", "baseurl": "http://controller1.example.com"})
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "baseurl": "http://controller1.example.com",
        "name": "New controller",
        "status": "unknown",
    }
    new_controller_id = response.json()["id"]
    response = client.delete(f"/api/controllers/{new_controller_id}")
    assert response.status_code == 204
    response = client.get(f"/api/controllers/{new_controller_id}")
    assert response.status_code == 404


def test_fail_delete_missing_controller(empty_database: None) -> None:  # noqa: ARG001
    """Test that deleting a non-existant controller fails."""
    client = TestClient(app)
    response = client.delete("/api/controllers/does-not-exist")
    assert response.status_code == 404
