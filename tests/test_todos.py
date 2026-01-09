"""Tests for Todo API endpoints."""

from fastapi.testclient import TestClient


def test_read_root(client: TestClient):
    """Test root endpoint redirects to docs."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_todo(client: TestClient):
    """Test creating a new todo."""
    todo_data = {
        "title": "Test Todo",
        "description": "Test description",
        "priority": 3,
    }
    response = client.post("/api/v1/todos/", json=todo_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == todo_data["title"]
    assert data["description"] == todo_data["description"]
    assert data["priority"] == todo_data["priority"]
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_todo_minimal(client: TestClient):
    """Test creating a todo with only required fields."""
    todo_data = {"title": "Minimal Todo"}
    response = client.post("/api/v1/todos/", json=todo_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == todo_data["title"]
    assert data["description"] is None
    assert data["priority"] == 1
    assert data["completed"] is False


def test_create_todo_invalid(client: TestClient):
    """Test creating a todo with invalid data."""
    # Empty title
    response = client.post("/api/v1/todos/", json={"title": ""})
    assert response.status_code == 422

    # Missing title
    response = client.post("/api/v1/todos/", json={})
    assert response.status_code == 422

    # Invalid priority
    response = client.post("/api/v1/todos/", json={"title": "Test", "priority": 10})
    assert response.status_code == 422


def test_read_todos_empty(client: TestClient):
    """Test reading todos when empty."""
    response = client.get("/api/v1/todos/")
    assert response.status_code == 200
    assert response.json() == []


def test_read_todos(client: TestClient):
    """Test reading all todos."""
    # Create some todos
    for i in range(3):
        client.post("/api/v1/todos/", json={"title": f"Todo {i}"})

    response = client.get("/api/v1/todos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_read_todos_pagination(client: TestClient):
    """Test pagination."""
    # Create 5 todos
    for i in range(5):
        client.post("/api/v1/todos/", json={"title": f"Todo {i}"})

    # Get first 2
    response = client.get("/api/v1/todos/?limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Get next 2
    response = client.get("/api/v1/todos/?offset=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_read_todos_filter_completed(client: TestClient):
    """Test filtering by completion status."""
    # Create completed and incomplete todos
    client.post("/api/v1/todos/", json={"title": "Incomplete", "completed": False})
    response = client.post(
        "/api/v1/todos/", json={"title": "Complete", "completed": True}
    )
    todo_id = response.json()["id"]
    client.patch(f"/api/v1/todos/{todo_id}", json={"completed": True})

    # Filter completed
    response = client.get("/api/v1/todos/?completed=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["completed"] is True


def test_read_todo(client: TestClient):
    """Test reading a specific todo."""
    # Create a todo
    create_response = client.post("/api/v1/todos/", json={"title": "Specific Todo"})
    todo_id = create_response.json()["id"]

    # Read it
    response = client.get(f"/api/v1/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Todo"


def test_read_todo_not_found(client: TestClient):
    """Test reading a non-existent todo."""
    response = client.get("/api/v1/todos/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


def test_update_todo(client: TestClient):
    """Test updating a todo."""
    # Create a todo
    create_response = client.post("/api/v1/todos/", json={"title": "Original"})
    todo_id = create_response.json()["id"]

    # Update it
    update_data = {"title": "Updated", "completed": True, "priority": 5}
    response = client.patch(f"/api/v1/todos/{todo_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["completed"] is True
    assert data["priority"] == 5


def test_update_todo_partial(client: TestClient):
    """Test partial update of a todo."""
    # Create a todo
    create_response = client.post(
        "/api/v1/todos/",
        json={"title": "Original", "description": "Original desc", "priority": 2},
    )
    todo_id = create_response.json()["id"]

    # Update only title
    response = client.patch(f"/api/v1/todos/{todo_id}", json={"title": "New Title"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "Original desc"
    assert data["priority"] == 2


def test_update_todo_not_found(client: TestClient):
    """Test updating a non-existent todo."""
    response = client.patch("/api/v1/todos/999", json={"title": "Updated"})
    assert response.status_code == 404


def test_delete_todo(client: TestClient):
    """Test deleting a todo."""
    # Create a todo
    create_response = client.post("/api/v1/todos/", json={"title": "To Delete"})
    todo_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/api/v1/todos/{todo_id}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/api/v1/todos/{todo_id}")
    assert response.status_code == 404


def test_delete_todo_not_found(client: TestClient):
    """Test deleting a non-existent todo."""
    response = client.delete("/api/v1/todos/999")
    assert response.status_code == 404
