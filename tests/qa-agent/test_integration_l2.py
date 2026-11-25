"""
QA Persona v2 -- auto-generated tests
Service: tasks-api-aspnetcore
Suite:   integration
Source:  test_strategy/plans/tasks-api-aspnetcore__integration.json
Generated: 2024-07-12T12:01:01.123456Z
"""
import os
import uuid
import pytest
import requests
from typing import List, Dict, Any

# Base URL for the service, determined by environment variable
BASE_URL = os.environ.get("TASKS_API_ASPNETCORE_URL", "http://localhost:8080").rstrip("/")

# --- Helper Functions ---

def delete_all_tasks():
    """Fetches all tasks and deletes them one by one to ensure a clean state."""
    try:
        resp = requests.get(f"{BASE_URL}/api/tasks", timeout=10)
        if resp.status_code == 200:
            tasks = resp.json()
            for task in tasks:
                requests.delete(f"{BASE_URL}/api/tasks/{task['id']}", timeout=5)
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Service is not available for cleanup: {e}")

def create_task_util(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Utility to create a task and return the response JSON."""
    resp = requests.post(f"{BASE_URL}/api/tasks", json=payload, timeout=5)
    resp.raise_for_status()  # Fail test if creation fails
    return resp.json()

# --- Fixtures ---

@pytest.fixture(scope="module", autouse=True)
def ensure_service_is_running():
    """Fixture to check if the service is running before starting tests."""
    try:
        requests.get(f"{BASE_URL}/api/tasks", timeout=5).raise_for_status()
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Task service not available at {BASE_URL}. Skipping integration tests. Error: {e}")

@pytest.fixture
def created_task():
    """Creates a single task and ensures it's cleaned up after the test."""
    task_id = None
    try:
        payload = {"title": f"Task {uuid.uuid4().hex}", "description": "A task for a test."}
        created = create_task_util(payload)
        task_id = created['id']
        yield created
    finally:
        if task_id:
            try:
                requests.delete(f"{BASE_URL}/api/tasks/{task_id}", timeout=5)
            except requests.exceptions.RequestException:
                # Ignore errors during cleanup
                pass

# --- Test Cases ---

def test_task_persistence_after_creation(created_task: Dict[str, Any]):
    """Verify that a created task is persisted and can be retrieved.

    test_id: tasks-api-aspnetcore__integration__001
    target: POST /api/tasks, GET /api/tasks/{id:int}
    requirement_id: REQ-BO,REQ-FR-PERSIST
    ac_ids: REQ-BO-AC-2,REQ-FR-PERSIST-AC-1,REQ-FR-PERSIST-AC-2,REQ-BO-AC-1,REQ-BO-AC-3
    """
    task_id = created_task['id']

    # Act: Retrieve the task by its ID
    resp = requests.get(f"{BASE_URL}/api/tasks/{task_id}", timeout=5)

    # Assert: The task is retrieved successfully and data matches
    assert resp.status_code == 200
    retrieved_task = resp.json()
    assert retrieved_task['id'] == created_task['id']
    assert retrieved_task['title'] == created_task['title']
    assert retrieved_task['description'] == created_task['description']

def test_updated_task_is_persisted(created_task: Dict[str, Any]):
    """Verify an updated task's changes are visible on a subsequent GET request.

    test_id: tasks-api-aspnetcore__integration__002
    target: PUT /api/tasks/{id:int}, GET /api/tasks/{id:int}
    requirement_id: REQ-FR-UPDATE,REQ-NFR
    ac_ids: REQ-FR-UPDATE-AC-2,REQ-FR-UPDATE-AC-3,REQ-NFR-AC-3
    """
    task_id = created_task['id']
    update_payload = {
        "title": "Updated Title",
        "description": "This description has been updated.",
        "isCompleted": True
    }

    # Act: Update the task
    update_resp = requests.put(f"{BASE_URL}/api/tasks/{task_id}", json=update_payload, timeout=5)
    assert update_resp.status_code == 204, "Update should return 204 No Content"

    # Act: Retrieve the task again
    get_resp = requests.get(f"{BASE_URL}/api/tasks/{task_id}", timeout=5)

    # Assert: The retrieved data reflects the updates
    assert get_resp.status_code == 200
    retrieved_task = get_resp.json()
    assert retrieved_task['title'] == update_payload['title']
    assert retrieved_task['description'] == update_payload['description']
    assert retrieved_task['isCompleted'] == update_payload['isCompleted']

def test_get_deleted_task_returns_404(created_task: Dict[str, Any]):
    """Verify a GET request for a deleted task returns 404 Not Found.

    test_id: tasks-api-aspnetcore__integration__003
    target: DELETE /api/tasks/{id:int}, GET /api/tasks/{id:int}
    requirement_id: REQ-FR-DELETE
    ac_ids: REQ-FR-DELETE-AC-2
    """
    task_id = created_task['id']

    # Act: Delete the task
    delete_resp = requests.delete(f"{BASE_URL}/api/tasks/{task_id}", timeout=5)
    assert delete_resp.status_code == 204, "Delete should return 204 No Content"

    # Act: Try to retrieve the deleted task
    get_resp = requests.get(f"{BASE_URL}/api/tasks/{task_id}", timeout=5)

    # Assert: The service returns 404 Not Found
    assert get_resp.status_code == 404

def test_list_tasks_ordered_by_id():
    """Verify that listing tasks returns them in a consistent order by ID.

    test_id: tasks-api-aspnetcore__integration__004
    target: GET /api/tasks
    requirement_id: REQ-FR-LIST,REQ-BO
    ac_ids: REQ-FR-LIST-AC-4,REQ-BO-AC-1,REQ-BO-AC-3
    """
    delete_all_tasks() # Ensure a clean slate for this test
    created_ids = []
    try:
        # Arrange: Create tasks in a non-sequential title order
        task_c = create_task_util({"title": "Task C"})
        task_a = create_task_util({"title": "Task A"})
        task_b = create_task_util({"title": "Task B"})
        created_ids = [task_c['id'], task_a['id'], task_b['id']]

        # Act: Get all tasks
        resp = requests.get(f"{BASE_URL}/api/tasks", timeout=5)
        assert resp.status_code == 200
        tasks = resp.json()
        retrieved_ids = [task['id'] for task in tasks]

        # Assert: The IDs are sorted in ascending order
        assert retrieved_ids == sorted(retrieved_ids)
    finally:
        # Cleanup
        for task_id in created_ids:
            requests.delete(f"{BASE_URL}/api/tasks/{task_id}", timeout=5)

def test_invalid_update_does_not_change_task(created_task: Dict[str, Any]):
    """Verify an invalid update request does not change the stored task.

    test_id: tasks-api-aspnetcore__integration__005
    target: PUT /api/tasks/{id:int}
    requirement_id: REQ-FR-UPDATE,REQ-NFR,REQ-BO
    ac_ids: REQ-FR-UPDATE-AC-5,REQ-NFR-AC-3,REQ-BO-AC-1,REQ-BO-AC-3
    """
    task_id = created_task['id']
    original_title = created_task['title']
    invalid_payload = {"description": "This update should fail"} # Missing required 'title'

    # Act: Attempt an invalid update
    update_resp = requests.put(f"{BASE_URL}/api/tasks/{task_id}", json=invalid_payload, timeout=5)
    assert update_resp.status_code == 400

    # Act: Retrieve the task to check if it was modified
    get_resp = requests.get(f"{BASE_URL}/api/tasks/{task_id}", timeout=5)
    assert get_resp.status_code == 200
    retrieved_task = get_resp.json()

    # Assert: The task data remains unchanged
    assert retrieved_task['title'] == original_title

def test_failed_create_leaves_no_partial_record():
    """Verify a failed create request does not leave a partial record in the database.

    test_id: tasks-api-aspnetcore__integration__006
    target: POST /api/tasks
    requirement_id: REQ-FR-CREATE,REQ-FR-PERSIST
    ac_ids: REQ-FR-CREATE-AC-6,REQ-FR-PERSIST-AC-4
    """
    # Arrange: Get initial task count
    initial_resp = requests.get(f"{BASE_URL}/api/tasks", timeout=5)
    assert initial_resp.status_code == 200
    initial_count = len(initial_resp.json())

    invalid_payload = {"description": "A task without a title"} # Missing required 'title'

    # Act: Attempt to create a task with invalid data
    create_resp = requests.post(f"{BASE_URL}/api/tasks", json=invalid_payload, timeout=5)
    assert create_resp.status_code == 400

    # Assert: The number of tasks has not changed
    final_resp = requests.get(f"{BASE_URL}/api/tasks", timeout=5)
    assert final_resp.status_code == 200
    final_count = len(final_resp.json())
    assert final_count == initial_count

def test_delete_one_task_does_not_affect_others():
    """Verify deleting one task does not affect other tasks.

    test_id: tasks-api-aspnetcore__integration__007
    target: DELETE /api/tasks/{id:int}
    requirement_id: REQ-FR-DELETE
    ac_ids: REQ-FR-DELETE-AC-3
    """
    task_a_id, task_b_id = None, None
    try:
        # Arrange: Create two tasks
        task_a_payload = {"title": "Task A to be deleted"}
        task_b_payload = {"title": "Task B to remain"}
        task_a = create_task_util(task_a_payload)
        task_b = create_task_util(task_b_payload)
        task_a_id, task_b_id = task_a['id'], task_b['id']

        # Act: Delete Task A
        delete_resp = requests.delete(f"{BASE_URL}/api/tasks/{task_a_id}", timeout=5)
        assert delete_resp.status_code == 204

        # Assert: Task A is gone, Task B is still there
        get_a_resp = requests.get(f"{BASE_URL}/api/tasks/{task_a_id}", timeout=5)
        assert get_a_resp.status_code == 404

        get_b_resp = requests.get(f"{BASE_URL}/api/tasks/{task_b_id}", timeout=5)
        assert get_b_resp.status_code == 200
        retrieved_b = get_b_resp.json()
        assert retrieved_b['id'] == task_b_id
        assert retrieved_b['title'] == task_b_payload['title']

    finally:
        # Cleanup the remaining task
        if task_b_id:
            requests.delete(f"{BASE_URL}/api/tasks/{task_b_id}", timeout=5)
