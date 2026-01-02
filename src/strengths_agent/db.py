"""DynamoDB client wrapper for CliftonStrengths profile management."""

import os
from typing import Any, Dict, List, Optional

import boto3
from boto3.dynamodb.conditions import Key


class DynamoDBClient:
    """Client for interacting with DynamoDB profiles table."""

    def __init__(self):
        """Initialize DynamoDB client with configuration from environment."""
        # Create session with profile if specified
        profile_name = os.getenv("AWS_PROFILE")
        if profile_name:
            session = boto3.Session(profile_name=profile_name)
            self.dynamodb = session.resource(
                "dynamodb",
                region_name=os.getenv("AWS_REGION", "us-east-1"),
            )
        else:
            self.dynamodb = boto3.resource(
                "dynamodb",
                region_name=os.getenv("AWS_REGION", "us-east-1"),
            )
        self.table_name = os.getenv("DYNAMODB_TABLE_NAME", "profiles")
        self.table = self.dynamodb.Table(self.table_name)

    def store_profile(
        self,
        first_name: str,
        last_name: str,
        email_address: str,
        strengths: List[str],
    ) -> Dict[str, Any]:
        """Store or update a CliftonStrengths profile.

        Args:
            first_name: Employee's first name
            last_name: Employee's last name
            email_address: Employee's email (unique identifier)
            strengths: List of 34 CliftonStrengths in ranked order

        Returns:
            Dict with success status and message
        """
        try:
            self.table.put_item(
                Item={
                    "email_address": email_address,
                    "first_name": first_name,
                    "last_name": last_name,
                    "strengths": strengths,
                }
            )
            return {
                "success": True,
                "message": f"Profile stored successfully for {first_name} {last_name} ({email_address})",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error storing profile: {str(e)}",
            }

    def get_profile_by_name(
        self, first_name: str, last_name: str
    ) -> Dict[str, Any]:
        """Retrieve CliftonStrengths profile(s) by name.

        Since first_name + last_name may not be unique, this may return
        multiple profiles.

        Args:
            first_name: Employee's first name
            last_name: Employee's last name

        Returns:
            Dict with profiles list and count
        """
        try:
            response = self.table.query(
                IndexName="name-index",
                KeyConditionExpression=Key("first_name").eq(first_name)
                & Key("last_name").eq(last_name),
            )

            profiles = response.get("Items", [])

            if not profiles:
                return {
                    "success": True,
                    "count": 0,
                    "message": f"No profile found for {first_name} {last_name}",
                    "profiles": [],
                }

            return {
                "success": True,
                "count": len(profiles),
                "message": f"Found {len(profiles)} profile(s) for {first_name} {last_name}",
                "profiles": profiles,
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving profile: {str(e)}",
                "profiles": [],
            }

    def get_all_profiles(self) -> Dict[str, Any]:
        """Retrieve all CliftonStrengths profiles from the database.

        Returns:
            Dict with all profiles and count
        """
        try:
            response = self.table.scan()
            profiles = response.get("Items", [])

            # Handle pagination if there are many profiles
            while "LastEvaluatedKey" in response:
                response = self.table.scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"]
                )
                profiles.extend(response.get("Items", []))

            return {
                "success": True,
                "count": len(profiles),
                "message": f"Retrieved {len(profiles)} profile(s) from the database",
                "profiles": profiles,
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving profiles: {str(e)}",
                "profiles": [],
            }


# Singleton instance
_db_client: Optional[DynamoDBClient] = None


def get_db_client() -> DynamoDBClient:
    """Get or create DynamoDB client singleton."""
    global _db_client
    if _db_client is None:
        _db_client = DynamoDBClient()
    return _db_client
