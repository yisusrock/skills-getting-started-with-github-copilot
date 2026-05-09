import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original = {
        name: {"participants": list(activity["participants"])}
        for name, activity in activities.items()
    }
    yield
    for name, activity in activities.items():
        activity["participants"] = list(original[name]["participants"])


def test_get_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_root_redirects_to_index_html():
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_signup_for_activity():
    email = "nuevo@mergington.edu"
    activity = "Chess Club"

    response = client.post(f"/activities/{activity}/signup?email={email}")

    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity}"


def test_signup_duplicate():
    email = "michael@mergington.edu"
    activity = "Chess Club"

    response = client.post(f"/activities/{activity}/signup?email={email}")

    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_activity_not_found():
    email = "nuevo@mergington.edu"
    activity = "NoExiste"

    response = client.post(f"/activities/{activity}/signup?email={email}")

    assert response.status_code == 404
    assert "activity not found" in response.json()["detail"].lower()


def test_remove_participant():
    email = "daniel@mergington.edu"
    activity = "Chess Club"

    response = client.delete(f"/activities/{activity}/participants/{email}")

    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_participant_not_found():
    email = "noexiste@mergington.edu"
    activity = "Chess Club"

    response = client.delete(f"/activities/{activity}/participants/{email}")

    assert response.status_code == 404
    assert "participant not found" in response.json()["detail"].lower()
