from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_all_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()
    assert "participants" in response.json()["Chess Club"]


def test_signup_for_activity_registers_new_participant():
    activity_name = "Soccer Club"
    email = "newstudent@mergington.edu"
    original_participants = activities[activity_name]["participants"][:]

    try:
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    finally:
        activities[activity_name]["participants"] = original_participants


def test_signup_for_activity_rejects_duplicate_participant():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_unknown_activity_returns_404():
    response = client.post("/activities/Unknown Club/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = "student@mergington.edu"
    original_participants = activities[activity_name]["participants"][:]

    try:
        activities[activity_name]["participants"].append(email)

        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    finally:
        activities[activity_name]["participants"] = original_participants


def test_unregister_missing_participant_returns_404():
    activity_name = "Chess Club"
    email = "missing@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
