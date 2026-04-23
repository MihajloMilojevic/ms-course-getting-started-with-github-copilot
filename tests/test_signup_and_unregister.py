from urllib.parse import quote

import src.app as app_module


def signup_url(activity_name):
    return f"/activities/{quote(activity_name, safe='')}/signup"


def test_signup_adds_participant_and_returns_success(client):
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    response = client.post(signup_url(activity_name), params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(signup_url("Unknown Club"), params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_returns_400_for_duplicate_participant(client):
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]

    response = client.post(signup_url(activity_name), params={"email": existing_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_removes_participant_and_returns_success(client):
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]

    response = client.delete(signup_url(activity_name), params={"email": existing_email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {existing_email} from {activity_name}"}
    assert existing_email not in app_module.activities[activity_name]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    response = client.delete(signup_url("Unknown Club"), params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_400_for_non_participant(client):
    activity_name = "Chess Club"
    not_registered_email = "not.registered@mergington.edu"

    response = client.delete(signup_url(activity_name), params={"email": not_registered_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up"


def test_signup_then_unregister_transitions_activity_state(client):
    activity_name = "Robotics Club"
    email = "flow.test@mergington.edu"

    signup_response = client.post(signup_url(activity_name), params={"email": email})
    assert signup_response.status_code == 200
    assert email in app_module.activities[activity_name]["participants"]

    unregister_response = client.delete(signup_url(activity_name), params={"email": email})
    assert unregister_response.status_code == 200
    assert email not in app_module.activities[activity_name]["participants"]
