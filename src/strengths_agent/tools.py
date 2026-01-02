"""This module provides tools for managing CliftonStrengths profiles in DynamoDB.

Tools allow storing and retrieving employee CliftonStrengths profiles.
"""

from typing import Any, Callable, Dict, List

from strengths_agent.db import get_db_client


def store_profile(
    first_name: str,
    last_name: str,
    email_address: str,
    strengths: List[str],
) -> Dict[str, Any]:
    """Store or update an employee's CliftonStrengths profile.

    This function stores a complete CliftonStrengths profile in the database.
    The profile includes the employee's name, email, and their ranked list
    of all 34 CliftonStrengths themes.

    Args:
        first_name: Employee's first name
        last_name: Employee's last name
        email_address: Employee's unique email address
        strengths: List of all 34 CliftonStrengths in ranked order (1-34)

    Returns:
        A dictionary containing:
        - success: Boolean indicating if the operation was successful
        - message: Description of the result
    """
    db = get_db_client()
    return db.store_profile(first_name, last_name, email_address, strengths)


def get_profile(first_name: str, last_name: str) -> Dict[str, Any]:
    """Retrieve an employee's CliftonStrengths profile by name.

    This function looks up CliftonStrengths profiles by first and last name.
    Note that multiple employees may share the same name, so this may return
    multiple profiles. Each profile includes the employee's email address to
    help distinguish between them.

    Args:
        first_name: Employee's first name
        last_name: Employee's last name

    Returns:
        A dictionary containing:
        - success: Boolean indicating if the operation was successful
        - count: Number of profiles found
        - message: Description of the result
        - profiles: List of matching profiles, each containing:
            - email_address: Employee's email
            - first_name: Employee's first name
            - last_name: Employee's last name
            - strengths: List of 34 CliftonStrengths in ranked order
    """
    db = get_db_client()
    return db.get_profile_by_name(first_name, last_name)


def get_all_profiles() -> Dict[str, Any]:
    """Retrieve all CliftonStrengths profiles from the database.

    This function retrieves every profile stored in the database, providing
    a complete list of all employees and their CliftonStrengths assessments.
    Useful for getting an overview of the entire organization's strengths.

    Returns:
        A dictionary containing:
        - success: Boolean indicating if the operation was successful
        - count: Total number of profiles in the database
        - message: Description of the result
        - profiles: List of all profiles, each containing:
            - email_address: Employee's email
            - first_name: Employee's first name
            - last_name: Employee's last name
            - strengths: List of 34 CliftonStrengths in ranked order
    """
    db = get_db_client()
    return db.get_all_profiles()


TOOLS: List[Callable[..., Any]] = [store_profile, get_profile, get_all_profiles]
