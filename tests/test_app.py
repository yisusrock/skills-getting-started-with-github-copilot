import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Utilidad para limpiar y restaurar el estado de las actividades
@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: guardar el estado original
    original = {k: v.copy() for k, v in activities.items()}
    for v in original.values():
        v["participants"] = list(v["participants"])
    yield
    # Restaurar
    for k in activities:
        activities[k]["participants"] = list(original[k]["participants"])


def test_get_activities():
    # Arrange
    # Nada que preparar
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_for_activity():
    # Arrange
    email = "nuevo@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_activity_not_found():
    # Arrange
    email = "nuevo@mergington.edu"
    activity = "NoExiste"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "activity not found" in response.json()["detail"].lower()


def test_remove_participant():
    # Arrange
    email = "daniel@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_participant_not_found():
    # Arrange
    email = "noexiste@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert
    assert response.status_code == 404
    assert "participant not found" in response.json()["detail"].lower()
