"""Unit tests for CliftonStrengths tools."""

from unittest.mock import MagicMock, patch

import pytest

from strengths_agent.tools import get_profile, store_profile


class TestStoreProfileTool:
    """Test suite for the store_profile tool."""

    @pytest.fixture
    def mock_db_client(self):
        """Create a mock database client."""
        with patch("strengths_agent.tools.get_db_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            yield mock_client

    def test_store_profile_success(self, mock_db_client):
        """Test storing a profile successfully."""
        mock_db_client.store_profile.return_value = {
            "success": True,
            "message": "Profile stored successfully for Arthur Torres (arthur@example.com)",
        }

        strengths = [f"Strength{i}" for i in range(1, 35)]
        result = store_profile(
            first_name="Arthur",
            last_name="Torres",
            email_address="arthur@example.com",
            strengths=strengths,
        )

        assert result["success"] is True
        assert "successfully" in result["message"].lower()
        mock_db_client.store_profile.assert_called_once_with(
            "Arthur", "Torres", "arthur@example.com", strengths
        )

    def test_store_profile_with_all_34_strengths(self, mock_db_client):
        """Test that store_profile accepts exactly 34 strengths."""
        mock_db_client.store_profile.return_value = {
            "success": True,
            "message": "Profile stored successfully",
        }

        all_strengths = [
            "Achiever", "Activator", "Adaptability", "Analytical", "Arranger",
            "Belief", "Command", "Communication", "Competition", "Connectedness",
            "Consistency", "Context", "Deliberative", "Developer", "Discipline",
            "Empathy", "Focus", "Futuristic", "Harmony", "Ideation",
            "Includer", "Individualization", "Input", "Intellection", "Learner",
            "Maximizer", "Positivity", "Relator", "Responsibility", "Restorative",
            "Self-Assurance", "Significance", "Strategic", "Woo",
        ]

        result = store_profile(
            first_name="Test",
            last_name="User",
            email_address="test@example.com",
            strengths=all_strengths,
        )

        assert result["success"] is True
        # Verify the tool passed the strengths list correctly
        call_args = mock_db_client.store_profile.call_args
        assert len(call_args[0][3]) == 34

    def test_store_profile_failure(self, mock_db_client):
        """Test handling of store profile failure."""
        mock_db_client.store_profile.return_value = {
            "success": False,
            "message": "Error storing profile: Connection timeout",
        }

        result = store_profile(
            first_name="Jane",
            last_name="Doe",
            email_address="jane@example.com",
            strengths=["Learner"] * 34,
        )

        assert result["success"] is False
        assert "error" in result["message"].lower()


class TestGetProfileTool:
    """Test suite for the get_profile tool."""

    @pytest.fixture
    def mock_db_client(self):
        """Create a mock database client."""
        with patch("strengths_agent.tools.get_db_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            yield mock_client

    def test_get_profile_found_single(self, mock_db_client):
        """Test retrieving a single profile."""
        mock_db_client.get_profile_by_name.return_value = {
            "success": True,
            "count": 1,
            "message": "Found 1 profile(s) for Arthur Torres",
            "profiles": [
                {
                    "email_address": "arthur@example.com",
                    "first_name": "Arthur",
                    "last_name": "Torres",
                    "strengths": ["Learner", "Achiever", "Strategic"] + ["Other"] * 31,
                }
            ],
        }

        result = get_profile("Arthur", "Torres")

        assert result["success"] is True
        assert result["count"] == 1
        assert len(result["profiles"]) == 1
        assert result["profiles"][0]["email_address"] == "arthur@example.com"
        mock_db_client.get_profile_by_name.assert_called_once_with("Arthur", "Torres")

    def test_get_profile_found_multiple(self, mock_db_client):
        """Test retrieving multiple profiles with the same name."""
        mock_db_client.get_profile_by_name.return_value = {
            "success": True,
            "count": 2,
            "message": "Found 2 profile(s) for John Smith",
            "profiles": [
                {
                    "email_address": "john.smith1@example.com",
                    "first_name": "John",
                    "last_name": "Smith",
                    "strengths": ["Learner"] * 34,
                },
                {
                    "email_address": "john.smith2@example.com",
                    "first_name": "John",
                    "last_name": "Smith",
                    "strengths": ["Achiever"] * 34,
                },
            ],
        }

        result = get_profile("John", "Smith")

        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["profiles"]) == 2
        # Verify both profiles have different email addresses
        emails = [p["email_address"] for p in result["profiles"]]
        assert "john.smith1@example.com" in emails
        assert "john.smith2@example.com" in emails

    def test_get_profile_not_found(self, mock_db_client):
        """Test retrieving a profile that doesn't exist."""
        mock_db_client.get_profile_by_name.return_value = {
            "success": True,
            "count": 0,
            "message": "No profile found for Nonexistent Person",
            "profiles": [],
        }

        result = get_profile("Nonexistent", "Person")

        assert result["success"] is True
        assert result["count"] == 0
        assert len(result["profiles"]) == 0
        assert "No profile found" in result["message"]

    def test_get_profile_error(self, mock_db_client):
        """Test handling of retrieval errors."""
        mock_db_client.get_profile_by_name.return_value = {
            "success": False,
            "message": "Error retrieving profile: Database unavailable",
            "profiles": [],
        }

        result = get_profile("Test", "User")

        assert result["success"] is False
        assert "error" in result["message"].lower()
        assert result["profiles"] == []

    def test_get_profile_returns_complete_strengths_list(self, mock_db_client):
        """Test that retrieved profiles contain all 34 strengths."""
        all_strengths = [f"Strength{i}" for i in range(1, 35)]
        
        mock_db_client.get_profile_by_name.return_value = {
            "success": True,
            "count": 1,
            "message": "Found 1 profile(s)",
            "profiles": [
                {
                    "email_address": "test@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "strengths": all_strengths,
                }
            ],
        }

        result = get_profile("Test", "User")

        assert len(result["profiles"][0]["strengths"]) == 34
