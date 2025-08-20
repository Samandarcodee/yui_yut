"""Tests for bot handlers and user flows."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.handlers import _sanitize_text, _spin_flow


@pytest.fixture
def mock_user_data():
    """Mock user data for testing."""
    return {
        "user_id": 12345,
        "username": "testuser",
        "stars": 100,
        "spins": 5,
        "biggest_win": 50,
        "is_banned": 0,
        "free_play": 0,
    }


@pytest.mark.asyncio
async def test_spin_flow_banned_user(mock_user_data):
    """Test that banned users cannot play."""
    mock_user_data["is_banned"] = 1

    # Mock database calls
    import src.db as db

    db.get_user = AsyncMock(return_value=mock_user_data)

    # Mock reply function
    reply_mock = AsyncMock()

    # Test spin flow
    await _spin_flow(12345, reply_mock)

    # Should get banned message
    reply_mock.assert_called_once_with("🚫 Bloklangansiz.")


@pytest.mark.asyncio
async def test_spin_flow_no_spins_no_stars(mock_user_data):
    """Test behavior when user has no spins and no stars."""
    mock_user_data["spins"] = 0
    mock_user_data["stars"] = 0

    import src.db as db

    db.get_user = AsyncMock(return_value=mock_user_data)

    reply_mock = AsyncMock()

    await _spin_flow(12345, reply_mock)

    # Should prompt to buy stars
    args, kwargs = reply_mock.call_args
    assert "Spinlar tugadi" in args[0]


def test_text_sanitization_comprehensive():
    """Comprehensive text sanitization test."""
    dangerous_inputs = [
        "<script>alert('xss')</script>",
        "javascript:void(0)",
        "data:text/html,<script>alert(1)</script>",
        "onclick=malicious_function()",
        "onload=steal_data()",
        "<img src=x onerror=alert(1)>",
    ]

    for dangerous_input in dangerous_inputs:
        sanitized = _sanitize_text(dangerous_input)
        # Should not contain dangerous patterns
        assert "javascript:" not in sanitized.lower()
        assert "onclick=" not in sanitized.lower()
        assert "<script" not in sanitized.lower()
        assert "onerror=" not in sanitized.lower()
