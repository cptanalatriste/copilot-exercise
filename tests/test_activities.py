"""Tests for FastAPI activity management endpoints"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a test client
client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        activity: {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": details["participants"].copy()
        }
        for activity, details in activities.items()
    }
    
    yield
    
    # Restore original state
    for activity, details in activities.items():
        details["participants"] = original_activities[activity]["participants"].copy()


class TestGetActivities:
    """Test suite for getting activities"""
    
    def test_get_activities_returns_200(self):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_all_activities(self):
        """Test that all activities are returned"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert "Art Studio" in data
        assert "Drama Club" in data
        assert "Debate Team" in data
        assert "Science Club" in data
    
    def test_get_activities_has_correct_structure(self):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity, details in data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)


class TestSignupForActivity:
    """Test suite for signing up for activities"""
    
    def test_signup_returns_200(self, reset_activities):
        """Test that signup returns status 200 on success"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_signup_adds_participant(self, reset_activities):
        """Test that signup adds participant to activity"""
        email = "newstudent@mergington.edu"
        initial_count = len(activities["Chess Club"]["participants"])
        
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        
        assert response.status_code == 200
        assert len(activities["Chess Club"]["participants"]) == initial_count + 1
        assert email in activities["Chess Club"]["participants"]
    
    def test_signup_returns_success_message(self, reset_activities):
        """Test that signup returns success message"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_for_nonexistent_activity_returns_404(self, reset_activities):
        """Test that signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_returns_400(self, reset_activities):
        """Test that signing up twice returns 400"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_different_activities(self, reset_activities):
        """Test signing up for multiple different activities"""
        email = "newstudent@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Test suite for unregistering from activities"""
    
    def test_unregister_returns_200(self, reset_activities):
        """Test that unregister returns status 200 on success"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
    
    def test_unregister_removes_participant(self, reset_activities):
        """Test that unregister removes participant from activity"""
        email = "michael@mergington.edu"
        initial_count = len(activities["Chess Club"]["participants"])
        
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        
        assert response.status_code == 200
        assert len(activities["Chess Club"]["participants"]) == initial_count - 1
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_returns_success_message(self, reset_activities):
        """Test that unregister returns success message"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_unregister_from_nonexistent_activity_returns_404(self, reset_activities):
        """Test that unregister from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_not_registered_returns_400(self, reset_activities):
        """Test that unregistering someone not registered returns 400"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_then_signup_again(self, reset_activities):
        """Test that participant can sign up again after unregistering"""
        email = "michael@mergington.edu"
        
        # Unregister
        response1 = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response1.status_code == 200
        assert email not in activities["Chess Club"]["participants"]
        
        # Sign up again
        response2 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response2.status_code == 200
        assert email in activities["Chess Club"]["participants"]


class TestRootRedirect:
    """Test suite for root endpoint"""
    
    def test_root_redirects_to_static(self):
        """Test that root redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
