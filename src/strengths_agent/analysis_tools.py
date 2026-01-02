"""Tools for analyzing and comparing CliftonStrengths profiles.

These tools perform analysis operations that don't require database access.
"""

from typing import Any, Callable, Dict, List


def compare_profiles(
    target_profile: Dict[str, Any],
    other_profiles: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compare a target profile against other profiles and rank by similarity.

    This function measures similarity between CliftonStrengths profiles by computing
    the distance between strength rankings. Lower distance means more similar profiles.

    Similarity is computed as the sum of absolute differences in rankings for each
    strength theme. Lower distance means more similar profiles.

    Args:
        target_profile: Dictionary containing the profile to compare against. Must include
            'first_name', 'last_name', and 'strengths' (list of 34 themes in ranked order).
        other_profiles: List of profile dictionaries to compare. Each must include
            'first_name', 'last_name', 'email_address', and 'strengths' (list of 34 themes).

    Returns:
        Dictionary with 'success' (bool), 'message' (str), 'target' (str), and 'comparisons'
        (list of profiles sorted by similarity, each with a 'similarity_score').
    """
    try:
        # Validate target profile
        if not target_profile.get("strengths"):
            return {
                "success": False,
                "message": "Target profile must include 'strengths' list",
            }

        target_strengths = target_profile["strengths"]
        if len(target_strengths) < 34:
            return {
                "success": False,
                "message": f"Target profile must include all 34 strengths, found {len(target_strengths)}",
            }

        # Build rank map for target profile
        target_ranks = {
            strength: rank + 1 for rank, strength in enumerate(target_strengths)
        }

        # Compute similarity for each profile
        comparisons = []
        for profile in other_profiles:
            if not profile.get("strengths"):
                continue

            profile_strengths = profile["strengths"]
            if len(profile_strengths) < 34:
                continue

            # Build rank map for this profile
            profile_ranks = {
                strength: rank + 1 for rank, strength in enumerate(profile_strengths)
            }

            # Compute distance (sum of absolute differences in ranks)
            distance = 0
            for strength in target_strengths:
                if strength in profile_ranks:
                    distance += abs(target_ranks[strength] - profile_ranks[strength])
                else:
                    # If a strength is missing, add maximum penalty
                    distance += 34

            # Add profile with similarity score
            comparisons.append(
                {
                    "first_name": profile.get("first_name", ""),
                    "last_name": profile.get("last_name", ""),
                    "email_address": profile.get("email_address", ""),
                    "strengths": profile_strengths,
                    "similarity_score": distance,
                }
            )

        # Sort by similarity score (ascending - lower is more similar)
        comparisons.sort(key=lambda x: x["similarity_score"])

        target_name = f"{target_profile.get('first_name', '')} {target_profile.get('last_name', '')}".strip()
        if not target_name:
            target_name = "Target Profile"

        return {
            "success": True,
            "message": f"Compared {len(comparisons)} profile(s) against {target_name}",
            "target": target_name,
            "comparisons": comparisons,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error comparing profiles: {str(e)}",
        }


ANALYSIS_TOOLS: List[Callable[..., Any]] = [compare_profiles]
