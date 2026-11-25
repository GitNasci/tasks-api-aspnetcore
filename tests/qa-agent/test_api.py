import os
import uuid
import requests
import pytest
import datetime
from urllib.parse import urljoin

"""
QA Persona v2 -- auto-generated tests
Service: tasks-api-aspnetcore
Suite:   api
Source:  test_strategy/plans/tasks-api-aspnetcore__api.json
Generated: 2024-07-12T12:00:00.000000Z
"""

# Get the base URL from the environment variable, with a fallback for local development
BASE_URL = os.environ.get("TASKS_API_ASPNETCORE_URL", "http://localhost:8080").rstrip("/")


def create_task_payload(title_prefix="Test Task"):
    """Helper to create a unique task payload."""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "title": f"{title_prefix} {unique_id}",
        "description": f"Description for task {unique_id}",
        "isCompleted": False
    }


@pytest.fixture(scope="function")
def created_task():
    """Creates a task for a test, yields the task data, and cleans up afterward."""
    payload = create_task_payload()
    create_response = requests.post(f"{BASE_URL}/api/tasks", json=payload)
    assert create_response.status_code == 201, f"Setup failed: Could not create task. Response: {create_response.text}"
    task_data = create_response.json()
    
    yield task_data
    
    # Teardown: delete the created task
    task_id = task_data.get("id")
    if task_id:
        requests.delete(f"{BASE_URL}/api/tasks/{task_id}")


def cleanup_all_tasks():
    """Deletes all tasks from the service to ensure a clean state."""
    try:
        response = requests.get(f"{BASE_URL}/api/tasks")
        if response.status_code == 200:
            tasks = response.json()
            for task in tasks:
                task_id = task.get("id")
                if task_id:
                    requests.delete(f"{BASE_URL}/api/tasks/{task_id}")
    except requests.exceptions.RequestException:
        # Ignore if the service is not reachable during cleanup
        pass


def test_create_a_task_with_a_valid_payload():
    """Verifies that a POST request to /api/tasks with a valid JSON body successfully creates a new task and returns a 201 Created status.

    test_id: tasks-api-aspnetcore__api__001
    target: POST /api/tasks
    requirement_id: REQ-SCOPE,REQ-DATA,REQ-FR-CREATE
    ac_ids: REQ-SCOPE-AC-1,REQ-FR-CREATE-AC-1,REQ-FR-CREATE-AC-3,REQ-DATA-AC-1,REQ-DATA-AC-2,REQ-DATA-AC-3,REQ-DATA-AC-4
    """
    payload = create_task_payload()
    response = requests.post(f"{BASE_URL}/api/tasks", json=payload)
    
    assert response.status_code == 201
    
    task_data = response.json()
    assert "id" in task_data
    assert isinstance(task_data["id"], int)
    assert task_data["title"] == payload["title"]
    assert task_data["description"] == payload["description"]
    assert task_data["isCompleted"] == payload["isCompleted"]
    assert "createdAt" in task_data

    # Cleanup
    task_id = task_data.get("id")
    if task_id:
        requests.delete(f"{BASE_URL}/api/tasks/{task_id}")


def test_list_all_created_tasks(created_task):
    """Verifies that a GET request to /api/tasks returns a 200 OK status and a list of all tasks.

    test_id: tasks-api-aspnetcore__api__002
    target: GET /api/tasks
    requirement_id: REQ-SCOPE,REQ-FR-LIST
    ac_ids: REQ-SCOPE-AC-2,REQ-FR-LIST-AC-1,REQ-FR-LIST-AC-3
    """
    response = requests.get(f"{BASE_URL}/api/tasks")
    
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert len(tasks) > 0
    # Check if our created task is in the list
    assert any(task['id'] == created_task['id'] for task in tasks)


def test_get_a_single_task_by_its_id(created_task):
    """Verifies that a GET request to /api/tasks/{id} with a valid ID returns 200 OK and the correct task.

    test_id: tasks-api-aspnetcore__api__003
    target: GET /api/tasks/{id:int}
    requirement_id: REQ-SCOPE,REQ-FR-READ
    ac_ids: REQ-SCOPE-AC-3,REQ-FR-READ-AC-1,REQ-FR-READ-AC-2
    """
    task_id = created_task["id"]
    response = requests.get(f"{BASE_URL}/api/tasks/{task_id}")
    
    assert response.status_code == 200
    task_data = response.json()
    assert task_data["id"] == task_id
    assert task_data["title"] == created_task["title"]


def test_update_an_existing_task_with_a_valid_payload(created_task):
    """Verifies that a PUT request to /api/tasks/{id} with a valid payload updates the task and returns 204 No Content.

    test_id: tasks-api-aspnetcore__api__004
    target: PUT /api/tasks/{id:int}
    requirement_id: REQ-SCOPE,REQ-FR-UPDATE
    ac_ids: REQ-SCOPE-AC-4,REQ-FR-UPDATE-AC-1
    """
    task_id = created_task["id"]
    update_payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "isCompleted": True
    }
    
    response = requests.put(f"{BASE_URL}/api/tasks/{task_id}", json=update_payload)
    
    # ASP.NET Core's NoContent() returns 204
    assert response.status_code == 204
    
    # Verify the update by fetching the task again
    get_response = requests.get(f"{BASE_URL}/api/tasks/{task_id}")
    assert get_response.status_code == 200
    updated_task = get_response.json()
    assert updated_task["title"] == update_payload["title"]
    assert updated_task["description"] == update_payload["description"]
    assert updated_task["isCompleted"] == update_payload["isCompleted"]


def test_delete_an_existing_task_by_its_id(created_task):
    """Verifies that a DELETE request to /api/tasks/{id} successfully deletes the task and returns 204 No Content.

    test_id: tasks-api-aspnetcore__api__005
    target: DELETE /api/tasks/{id:int}
    requirement_id: REQ-SCOPE,REQ-FR-DELETE
    ac_ids: REQ-SCOPE-AC-5,REQ-FR-DELETE-AC-1
    """
    task_id = created_task["id"]
    
    response = requests.delete(f"{BASE_URL}/api/tasks/{task_id}")
    
    # ASP.NET Core's NoContent() returns 204
    assert response.status_code == 204
    
    # Verify deletion by trying to fetch the task again
    get_response = requests.get(f"{BASE_URL}/api/tasks/{task_id}")
    assert get_response.status_code == 404


def test_reject_creating_a_task_with_a_missing_required_title():
    """Verifies that the API rejects a POST request with a missing 'title' field and returns a 400-series client error.

    test_id: tasks-api-aspnetcore__api__006_negative_missing_field
    target: POST /api/tasks
    requirement_id: REQ-BO,REQ-FR-CREATE,REQ-FR-VALIDATE,REQ-SEC
    ac_ids: REQ-BO-AC-4,REQ-FR-CREATE-AC-4,REQ-FR-CREATE-AC-6,REQ-FR-VALIDATE-AC-2,REQ-SEC-AC-1
    """
    payload = {"description": "This task is missing a title"}
    response = requests.post(f"{BASE_URL}/api/tasks", json=payload)
    
    assert response.status_code == 400
    error_data = response.json()
    assert "errors" in error_data
    assert "Title" in error_data["errors"]


def test_return_404_not_found_when_getting_a_non_existent_task():
    """Verifies that a GET request to /api/tasks/{id} for an ID that does not exist returns a 404 Not Found status.

    test_id: tasks-api-aspnetcore__api__007_negative_not_found
    target: GET /api/tasks/{id:int}
    requirement_id: REQ-FR-READ,REQ-FR-VALIDATE
    ac_ids: REQ-FR-READ-AC-3,REQ-FR-VALIDATE-AC-4
    """
    non_existent_id = 999999
    response = requests.get(f"{BASE_URL}/api/tasks/{non_existent_id}")
    assert response.status_code == 404


def test_return_404_not_found_when_updating_a_non_existent_task():
    """Verifies that a PUT request to /api/tasks/{id} for an ID that does not exist returns a 404 Not Found status.

    test_id: tasks-api-aspnetcore__api__008_negative_not_found
    target: PUT /api/tasks/{id:int}
    requirement_id: REQ-FR-UPDATE
    ac_ids: REQ-FR-UPDATE-AC-4
    """
    non_existent_id = 999999
    payload = create_task_payload()
    response = requests.put(f"{BASE_URL}/api/tasks/{non_existent_id}", json=payload)
    assert response.status_code == 404


def test_return_404_not_found_when_deleting_a_non_existent_task():
    """Verifies that a DELETE request to /api/tasks/{id} for an ID that does not exist returns a 404 Not Found status.

    test_id: tasks-api-aspnetcore__api__009_negative_not_found
    target: DELETE /api/tasks/{id:int}
    requirement_id: REQ-FR-DELETE
    ac_ids: REQ-FR-DELETE-AC-4
    """
    non_existent_id = 999999
    response = requests.delete(f"{BASE_URL}/api/tasks/{non_existent_id}")
    assert response.status_code == 404


def test_return_client_error_for_a_malformed_task_id_in_url():
    """Verifies that the API rejects requests with a non-integer ID in the URL path, due to the route constraint.

    test_id: tasks-api-aspnetcore__api__010_negative_malformed_id
    target: GET /api/tasks/{id:int}
    requirement_id: REQ-FR-READ
    ac_ids: REQ-FR-READ-AC-4
    """
    malformed_id = "abc"
    response = requests.get(f"{BASE_URL}/api/tasks/{malformed_id}")
    # ASP.NET Core route constraints cause a 404 when the type doesn't match
    assert response.status_code == 404


def test_verify_iscompleted_defaults_to_false_when_not_provided():
    """Tests that when a new task is created without specifying 'isCompleted', the system defaults the value to false.

    test_id: tasks-api-aspnetcore__api__011
    target: POST /api/tasks
    requirement_id: REQ-FR-CREATE
    ac_ids: REQ-FR-CREATE-AC-5
    """
    payload = {"title": "Task with default completion"}
    response = requests.post(f"{BASE_URL}/api/tasks", json=payload)
    assert response.status_code == 201
    
    created_task = response.json()
    task_id = created_task["id"]
    
    # Verify the default value by fetching the task
    get_response = requests.get(f"{BASE_URL}/api/tasks/{task_id}")
    assert get_response.status_code == 200
    fetched_task = get_response.json()
    assert fetched_task["isCompleted"] is False

    # Cleanup
    requests.delete(f"{BASE_URL}/api/tasks/{task_id}")


def test_verify_listing_tasks_from_an_empty_database_returns_empty_list():
    """Ensures that GET /api/tasks returns a 200 OK with an empty array when no tasks exist, rather than an error.

    test_id: tasks-api-aspnetcore__api__012
    target: GET /api/tasks
    requirement_id: REQ-FR-LIST
    ac_ids: REQ-FR-LIST-AC-2
    """
    # Ensure the database is empty for this test
    cleanup_all_tasks()
    
    response = requests.get(f"{BASE_URL}/api/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_reject_a_request_with_malformed_json():
    """Verifies that the API returns a 400 Bad Request error when the request body is not valid JSON.

    test_id: tasks-api-aspnetcore__api__013_negative_invalid_json
    target: POST /api/tasks
    requirement_id: REQ-FR-VALIDATE
    ac_ids: REQ-FR-VALIDATE-AC-1
    """
    headers = {"Content-Type": "application/json"}
    malformed_json_body = '{"title": "My Task", "description": "A description"' # Missing closing brace
    
    response = requests.post(f"{BASE_URL}/api/tasks", data=malformed_json_body, headers=headers)
    assert response.status_code == 400


def test_reject_a_request_with_incorrect_field_types():
    """Verifies that the API returns a 400 Bad Request error when a field has the wrong data type (e.g., a string for a boolean).

    test_id: tasks-api-aspnetcore__api__014_negative_wrong_type
    target: POST /api/tasks
    requirement_id: REQ-FR-VALIDATE
    ac_ids: REQ-FR-VALIDATE-AC-3
    """
    payload = {"title": "My Task", "isCompleted": "true"} # isCompleted should be a boolean
    response = requests.post(f"{BASE_URL}/api/tasks", json=payload)
    assert response.status_code == 400


def test_verify_api_contract_for_get_api_tasks_id(created_task):
    """API contract smoke test verifying HTTP status and response schema for GET /api/tasks/{id:int}.

    test_id: tasks-api-aspnetcore__api__015
    target: GET /api/tasks/{id:int}
    requirement_id: no requirement
    ac_ids: none
    """
    task_id = created_task["id"]
    response = requests.get(f"{BASE_URL}/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert all(k in data for k in ["id", "title", "description", "isCompleted", "createdAt"])


def test_verify_api_contract_for_put_api_tasks_id(created_task):
    """API contract smoke test verifying HTTP status and response schema for PUT /api/tasks/{id:int}.

    test_id: tasks-api-aspnetcore__api__016
    target: PUT /api/tasks/{id:int}
    requirement_id: no requirement
    ac_ids: none
    """
    task_id = created_task["id"]
    payload = {"title": "Contract Update", "description": "...", "isCompleted": True}
    response = requests.put(f"{BASE_URL}/api/tasks/{task_id}", json=payload)
    assert response.status_code == 204
    assert not response.text # Expect empty body for 204 No Content


def test_verify_api_contract_for_delete_api_tasks_id(created_task):
    """API contract smoke test verifying HTTP status and response schema for DELETE /api/tasks/{id:int}.

    test_id: tasks-api-aspnetcore__api__017
    target: DELETE /api/tasks/{id:int}
    requirement_id: no requirement
    ac_ids: none
    """
    task_id = created_task["id"]
    response = requests.delete(f"{BASE_URL}/api/tasks/{task_id}")
    assert response.status_code == 204
    assert not response.text # Expect empty body for 204 No Content


def test_negative_verify_http_404_error_handling_on_get_api_tasks_id():
    """Negative-path API test verifying that GET /api/tasks/{id:int} returns HTTP 404 when called with invalid parameters or non-existent resource identifiers.

    test_id: tasks-api-aspnetcore__api__018_negative
    target: GET /api/tasks/{id:int}
    requirement_id: no requirement
    ac_ids: none
    """
    non_existent_id = 999999
    response = requests.get(f"{BASE_URL}/api/tasks/{non_existent_id}")
    assert response.status_code == 404


def test_negative_verify_http_404_error_handling_on_put_api_tasks_id():
    """Negative-path API test verifying that PUT /api/tasks/{id:int} returns HTTP 404 when called with invalid parameters or non-existent resource identifiers.

    test_id: tasks-api-aspnetcore__api__019_negative
    target: PUT /api/tasks/{id:int}
    requirement_id: no requirement
    ac_ids: none
    """
    non_existent_id = 999999
    payload = create_task_payload()
    response = requests.put(f"{BASE_URL}/api/tasks/{non_existent_id}", json=payload)
    assert response.status_code == 404


def test_negative_verify_http_404_error_handling_on_delete_api_tasks_id():
    """Negative-path API test verifying that DELETE /api/tasks/{id:int} returns HTTP 404 when called with invalid parameters or non-existent resource identifiers.

    test_id: tasks-api-aspnetcore__api__020_negative
    target: DELETE /api/tasks/{id:int}
    requirement_id: no requirement
    ac_ids: none
    """
    non_existent_id = 999999
    response = requests.delete(f"{BASE_URL}/api/tasks/{non_existent_id}")
    assert response.status_code == 404
