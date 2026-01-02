"""Unit tests for CliftonStrengths analysis tools."""

import pytest

from strengths_agent.analysis_tools import compare_profiles


class TestCompareProfilesTool:
    """Test suite for the compare_profiles tool."""

    def test_compare_profiles_success(self):
        """Test comparing profiles successfully."""
        target = {
            "first_name": "Alice",
            "last_name": "Smith",
            "strengths": [f"Strength{i}" for i in range(1, 35)],
        }

        others = [
            {
                "first_name": "Bob",
                "last_name": "Jones",
                "email_address": "bob@example.com",
                "strengths": [f"Strength{i}" for i in range(1, 35)],  # Identical
            },
            {
                "first_name": "Charlie",
                "last_name": "Brown",
                "email_address": "charlie@example.com",
                "strengths": [f"Strength{i}" for i in range(2, 36)],  # Different
            },
        ]

        result = compare_profiles(target, others)

        assert result["success"] is True
        assert result["target"] == "Alice Smith"
        assert len(result["comparisons"]) == 2
        # Bob should be more similar (score 0) than Charlie
        assert result["comparisons"][0]["email_address"] == "bob@example.com"
        assert result["comparisons"][0]["similarity_score"] == 0
        assert result["comparisons"][1]["similarity_score"] > 0

    def test_compare_profiles_sorted_by_similarity(self):
        """Test that results are sorted by similarity score."""
        target = {
            "first_name": "Target",
            "last_name": "User",
            "strengths": ["Achiever", "Learner", "Strategic"] + [f"S{i}" for i in range(4, 35)],
        }

        others = [
            {
                "first_name": "Very Different",
                "last_name": "Person",
                "email_address": "different@example.com",
                # Completely reversed order
                "strengths": list(reversed(["Achiever", "Learner", "Strategic"] + [f"S{i}" for i in range(4, 35)])),
            },
            {
                "first_name": "Very Similar",
                "last_name": "Person",
                "email_address": "similar@example.com",
                # Identical
                "strengths": ["Achiever", "Learner", "Strategic"] + [f"S{i}" for i in range(4, 35)],
            },
            {
                "first_name": "Somewhat Similar",
                "last_name": "Person",
                "email_address": "somewhat@example.com",
                # Slightly different (swap first two)
                "strengths": ["Learner", "Achiever", "Strategic"] + [f"S{i}" for i in range(4, 35)],
            },
        ]

        result = compare_profiles(target, others)

        assert result["success"] is True
        assert len(result["comparisons"]) == 3
        
        # Check ordering: similar < somewhat < different
        assert result["comparisons"][0]["email_address"] == "similar@example.com"
        assert result["comparisons"][1]["email_address"] == "somewhat@example.com"
        assert result["comparisons"][2]["email_address"] == "different@example.com"
        
        # Check scores are in ascending order
        scores = [c["similarity_score"] for c in result["comparisons"]]
        assert scores[0] < scores[1] < scores[2]

    def test_compare_profiles_identical_profiles(self):
        """Test comparing identical profiles returns score of 0."""
        target = {
            "first_name": "Alice",
            "last_name": "Smith",
            "strengths": ["Achiever", "Learner", "Strategic"] + [f"S{i}" for i in range(4, 35)],
        }

        others = [
            {
                "first_name": "Bob",
                "last_name": "Jones",
                "email_address": "bob@example.com",
                "strengths": ["Achiever", "Learner", "Strategic"] + [f"S{i}" for i in range(4, 35)],
            }
        ]

        result = compare_profiles(target, others)

        assert result["success"] is True
        assert result["comparisons"][0]["similarity_score"] == 0

    def test_compare_profiles_single_swap(self):
        """Test that swapping two adjacent strengths creates expected distance."""
        target = {
            "first_name": "Alice",
            "last_name": "Smith",
            "strengths": ["Achiever", "Learner"] + [f"S{i}" for i in range(3, 35)],
        }

        others = [
            {
                "first_name": "Bob",
                "last_name": "Jones",
                "email_address": "bob@example.com",
                # Swap first two: Achiever goes from rank 1 to 2 (+1), Learner goes from rank 2 to 1 (-1)
                # Distance = |1-2| + |2-1| = 1 + 1 = 2
                "strengths": ["Learner", "Achiever"] + [f"S{i}" for i in range(3, 35)],
            }
        ]

        result = compare_profiles(target, others)

        assert result["success"] is True
        assert result["comparisons"][0]["similarity_score"] == 2

    def test_compare_profiles_missing_target_strengths(self):
        """Test error when target profile lacks strengths."""
        target = {
            "first_name": "Alice",
            "last_name": "Smith",
        }

        others = [
            {
                "first_name": "Bob",
                "last_name": "Jones",
                "email_address": "bob@example.com",
                "strengths": [f"S{i}" for i in range(1, 35)],
            }
        ]

        result = compare_profiles(target, others)

        assert result["success"] is False
        assert "must include 'strengths' list" in result["message"]

    def test_compare_profiles_incomplete_target_strengths(self):
        """Test error when target profile has fewer than 34 strengths."""
        target = {
            "first_name": "Alice",
            "last_name": "Smith",
            "strengths": ["Achiever", "Learner", "Strategic"],  # Only 3
        }

        others = [
            {
                "first_name": "Bob",
                "last_name": "Jones",
                "email_address": "bob@example.com",
                "strengths": [f"S{i}" for i in range(1, 35)],
            }
        ]

        result = compare_profiles(target, others)

        assert result["success"] is False
        assert "must include all 34 strengths" in result["message"]
        assert "found 3" in result["message"]

    def test_compare_profiles_skip_incomplete_other_profiles(self):
        """Test that profiles with incomplete strengths are skipped."""
        target = {
            "first_name": "Alice",
            "last_name": "Smith",
            "strengths": [f"S{i}" for i in range(1, 35)],
        }

        others = [
            {
                "first_name": "Bob",
                "last_name": "Jones",
                "email_address": "bob@example.com",
                "strengths": [f"S{i}" for i in range(1, 35)],
            },
            {
                "first_name": "Incomplete",
                "last_name": "Profile",
                "email_address": "incomplete@example.com",
                "strengths": ["Achiever", "Learner"],  # Only 2
            },
            {
                "first_name": "No Strengths",
                "last_name": "Profile",
                "email_address": "none@example.com",
            },
        ]

        result = compare_profiles(target, others)

        assert result["success"] is True
        assert len(result["comparisons"]) == 1
        assert result["comparisons"][0]["email_address"] == "bob@example.com"

    def test_compare_profiles_empty_other_profiles(self):
        """Test comparing with an empty list of other profiles."""
        target = {
            "first_name": "Alice",
            "last_name": "Smith",
            "strengths": [f"S{i}" for i in range(1, 35)],
        }

        result = compare_profiles(target, [])

        assert result["success"] is True
        assert len(result["comparisons"]) == 0
        assert "Compared 0 profile" in result["message"]

    def test_compare_profiles_target_without_name(self):
        """Test target profile without name fields."""
        target = {
            "strengths": [f"S{i}" for i in range(1, 35)],
        }

        others = [
            {
                "first_name": "Bob",
                "last_name": "Jones",
                "email_address": "bob@example.com",
                "strengths": [f"S{i}" for i in range(1, 35)],
            }
        ]

        result = compare_profiles(target, others)

        assert result["success"] is True
        assert result["target"] == "Target Profile"

    def test_compare_profiles_all_fields_included(self):
        """Test that all profile fields are included in results."""
        target = {
            "first_name": "Alice",
            "last_name": "Smith",
            "strengths": [f"S{i}" for i in range(1, 35)],
        }

        others = [
            {
                "first_name": "Bob",
                "last_name": "Jones",
                "email_address": "bob@example.com",
                "strengths": [f"S{i}" for i in range(1, 35)],
            }
        ]

        result = compare_profiles(target, others)

        assert result["success"] is True
        comparison = result["comparisons"][0]
        assert "first_name" in comparison
        assert "last_name" in comparison
        assert "email_address" in comparison
        assert "strengths" in comparison
        assert "similarity_score" in comparison
        assert comparison["first_name"] == "Bob"
        assert comparison["last_name"] == "Jones"
        assert comparison["email_address"] == "bob@example.com"
        assert len(comparison["strengths"]) == 34

    def test_compare_profiles_large_distance(self):
        """Test profiles with maximum possible distance."""
        # Create completely opposite profiles
        strengths = [f"S{i}" for i in range(1, 35)]
        target = {
            "first_name": "Alice",
            "last_name": "Smith",
            "strengths": strengths,
        }

        others = [
            {
                "first_name": "Bob",
                "last_name": "Jones",
                "email_address": "bob@example.com",
                "strengths": list(reversed(strengths)),
            }
        ]

        result = compare_profiles(target, others)

        assert result["success"] is True
        # For reversed profiles, the distance is maximized
        # Each strength at position i moves to position (34-i)
        # For a 34-item list reversed, distance = sum of |i - (35-i)| for i=1..34
        # This equals sum of |2i - 35| for i=1..34
        assert result["comparisons"][0]["similarity_score"] > 0
