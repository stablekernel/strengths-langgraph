"""Unit tests for DynamoDB client functionality."""

import os
from unittest.mock import MagicMock, patch

import pytest

from strengths_agent.db import DynamoDBClient, get_db_client


class TestDynamoDBClient:
    """Test suite for DynamoDB client operations."""

    @pytest.fixture
    def mock_dynamodb_resource(self):
        """Create a mock DynamoDB resource."""
        with patch("strengths_agent.db.boto3") as mock_boto3:
            mock_resource = MagicMock()
            mock_table = MagicMock()
            mock_resource.Table.return_value = mock_table
            mock_boto3.resource.return_value = mock_resource
            mock_boto3.Session.return_value.resource.return_value = mock_resource
            yield mock_boto3, mock_table

    @pytest.fixture
    def db_client(self, mock_dynamodb_resource):
        """Create a DynamoDB client instance with mocked AWS connection."""
        _, _ = mock_dynamodb_resource
        with patch.dict(os.environ, {"DYNAMODB_TABLE_NAME": "test-profiles"}):
            return DynamoDBClient()

    def test_client_initialization_without_profile(self, mock_dynamodb_resource):
        """Test client initializes correctly without AWS profile."""
        mock_boto3, _ = mock_dynamodb_resource
        with patch.dict(os.environ, {"AWS_REGION": "us-west-2", "DYNAMODB_TABLE_NAME": "test-profiles"}, clear=True):
            client = DynamoDBClient()
            mock_boto3.resource.assert_called_once_with("dynamodb", region_name="us-west-2")
            assert client.table_name == "test-profiles"

    def test_client_initialization_with_profile(self, mock_dynamodb_resource):
        """Test client initializes correctly with AWS profile."""
        mock_boto3, _ = mock_dynamodb_resource
        with patch.dict(os.environ, {"AWS_PROFILE": "test-profile", "AWS_REGION": "us-east-1"}):
            client = DynamoDBClient()
            mock_boto3.Session.assert_called_once_with(profile_name="test-profile")

    def test_store_profile_success(self, db_client, mock_dynamodb_resource):
        """Test successfully storing a profile."""
        _, mock_table = mock_dynamodb_resource
        mock_table.put_item.return_value = {}

        strengths = [f"Strength{i}" for i in range(1, 35)]
        result = db_client.store_profile(
            first_name="John",
            last_name="Doe",
            email_address="john.doe@example.com",
            strengths=strengths,
        )

        assert result["success"] is True
        assert "successfully" in result["message"].lower()
        assert "John Doe" in result["message"]
        
        # Verify put_item was called with correct data
        mock_table.put_item.assert_called_once()
        call_args = mock_table.put_item.call_args
        assert call_args[1]["Item"]["first_name"] == "John"
        assert call_args[1]["Item"]["last_name"] == "Doe"
        assert call_args[1]["Item"]["email_address"] == "john.doe@example.com"
        assert len(call_args[1]["Item"]["strengths"]) == 34

    def test_store_profile_failure(self, db_client, mock_dynamodb_resource):
        """Test handling of store profile failure."""
        _, mock_table = mock_dynamodb_resource
        mock_table.put_item.side_effect = Exception("DynamoDB error")

        result = db_client.store_profile(
            first_name="Jane",
            last_name="Smith",
            email_address="jane.smith@example.com",
            strengths=["Learner"] * 34,
        )

        assert result["success"] is False
        assert "error" in result["message"].lower()
        assert "DynamoDB error" in result["message"]

    def test_get_profile_by_name_found_single(self, db_client, mock_dynamodb_resource):
        """Test retrieving a single profile by name."""
        _, mock_table = mock_dynamodb_resource
        
        mock_profile = {
            "email_address": "john.doe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "strengths": [f"Strength{i}" for i in range(1, 35)],
        }
        mock_table.query.return_value = {"Items": [mock_profile]}

        result = db_client.get_profile_by_name("John", "Doe")

        assert result["success"] is True
        assert result["count"] == 1
        assert len(result["profiles"]) == 1
        assert result["profiles"][0]["email_address"] == "john.doe@example.com"
        assert "Found 1 profile" in result["message"]

    def test_get_profile_by_name_found_multiple(self, db_client, mock_dynamodb_resource):
        """Test retrieving multiple profiles with same name."""
        _, mock_table = mock_dynamodb_resource
        
        mock_profiles = [
            {
                "email_address": "john.doe1@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "strengths": ["Learner"] * 34,
            },
            {
                "email_address": "john.doe2@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "strengths": ["Achiever"] * 34,
            },
        ]
        mock_table.query.return_value = {"Items": mock_profiles}

        result = db_client.get_profile_by_name("John", "Doe")

        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["profiles"]) == 2
        assert "Found 2 profile" in result["message"]

    def test_get_profile_by_name_not_found(self, db_client, mock_dynamodb_resource):
        """Test retrieving a profile that doesn't exist."""
        _, mock_table = mock_dynamodb_resource
        mock_table.query.return_value = {"Items": []}

        result = db_client.get_profile_by_name("Nonexistent", "Person")

        assert result["success"] is True
        assert result["count"] == 0
        assert len(result["profiles"]) == 0
        assert "No profile found" in result["message"]

    def test_get_profile_by_name_query_error(self, db_client, mock_dynamodb_resource):
        """Test handling of query errors."""
        _, mock_table = mock_dynamodb_resource
        mock_table.query.side_effect = Exception("Query failed")

        result = db_client.get_profile_by_name("John", "Doe")

        assert result["success"] is False
        assert "error" in result["message"].lower()
        assert "Query failed" in result["message"]
        assert result["profiles"] == []

    def test_get_all_profiles_success(self, db_client, mock_dynamodb_resource):
        """Test retrieving all profiles successfully."""
        _, mock_table = mock_dynamodb_resource
        
        mock_profiles = [
            {
                "email_address": "alice@example.com",
                "first_name": "Alice",
                "last_name": "Smith",
                "strengths": [f"Strength{i}" for i in range(1, 35)],
            },
            {
                "email_address": "bob@example.com",
                "first_name": "Bob",
                "last_name": "Jones",
                "strengths": ["Learner"] * 34,
            },
        ]
        mock_table.scan.return_value = {"Items": mock_profiles}

        result = db_client.get_all_profiles()

        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["profiles"]) == 2
        assert "Retrieved 2 profile" in result["message"]

    def test_get_all_profiles_with_pagination(self, db_client, mock_dynamodb_resource):
        """Test retrieving all profiles with pagination."""
        _, mock_table = mock_dynamodb_resource
        
        first_batch = [
            {
                "email_address": "user1@example.com",
                "first_name": "User",
                "last_name": "One",
                "strengths": ["Achiever"] * 34,
            }
        ]
        second_batch = [
            {
                "email_address": "user2@example.com",
                "first_name": "User",
                "last_name": "Two",
                "strengths": ["Learner"] * 34,
            }
        ]
        
        # Mock pagination
        mock_table.scan.side_effect = [
            {"Items": first_batch, "LastEvaluatedKey": {"email_address": "user1@example.com"}},
            {"Items": second_batch},
        ]

        result = db_client.get_all_profiles()

        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["profiles"]) == 2
        assert mock_table.scan.call_count == 2

    def test_get_all_profiles_empty(self, db_client, mock_dynamodb_resource):
        """Test retrieving all profiles when database is empty."""
        _, mock_table = mock_dynamodb_resource
        
        mock_table.scan.return_value = {"Items": []}

        result = db_client.get_all_profiles()

        assert result["success"] is True
        assert result["count"] == 0
        assert len(result["profiles"]) == 0
        assert "Retrieved 0 profile" in result["message"]

    def test_get_all_profiles_error(self, db_client, mock_dynamodb_resource):
        """Test error handling when scan fails."""
        _, mock_table = mock_dynamodb_resource
        
        mock_table.scan.side_effect = Exception("Scan failed")

        result = db_client.get_all_profiles()

        assert result["success"] is False
        assert "error" in result["message"].lower()
        assert "Scan failed" in result["message"]
        assert result["profiles"] == []


class TestGetDBClient:
    """Test suite for the get_db_client singleton function."""

    def test_get_db_client_singleton(self):
        """Test that get_db_client returns the same instance."""
        with patch("strengths_agent.db.boto3"):
            # Reset the singleton
            import strengths_agent.db
            strengths_agent.db._db_client = None
            
            client1 = get_db_client()
            client2 = get_db_client()
            
            assert client1 is client2

    def test_get_db_client_creates_instance(self):
        """Test that get_db_client creates an instance if none exists."""
        with patch("strengths_agent.db.boto3"):
            # Reset the singleton
            import strengths_agent.db
            strengths_agent.db._db_client = None
            
            client = get_db_client()
            
            assert client is not None
            assert isinstance(client, DynamoDBClient)
