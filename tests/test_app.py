import os
import sys
from urllib.parse import quote

# Ensure src directory is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastapi.testclient import TestClient
from app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure a clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up
    resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")
    assert email in activities[activity]["participants"]

    # Duplicate signup should fail
    resp_dup = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp_dup.status_code == 400

    # Unregister
    resp_un = client.post(f"/activities/{quote(activity)}/unregister?email={quote(email)}")
    assert resp_un.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_not_signed():
    activity = "Programming Class"
    email = "nonexistent@example.com"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.post(f"/activities/{quote(activity)}/unregister?email={quote(email)}")
    assert resp.status_code == 400
