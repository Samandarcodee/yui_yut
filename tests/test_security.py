"""Security tests for input validation and sanitization."""

import pytest

from src.handlers import _sanitize_text


def test_sanitize_text_basic():
    """Test basic text sanitization."""
    assert _sanitize_text("Hello World") == "Hello World"
    assert _sanitize_text("  spaced  ") == "spaced"
    assert _sanitize_text("") == ""


def test_sanitize_text_html_removal():
    """Test HTML tag removal."""
    assert _sanitize_text("<script>alert('xss')</script>") == "alert('xss')"
    assert _sanitize_text("<b>Bold</b> text") == "Bold text"
    assert _sanitize_text("<img src='x' onerror='alert(1)'>") == ""


def test_sanitize_text_length_limit():
    """Test length limiting."""
    long_text = "a" * 2000
    result = _sanitize_text(long_text, max_length=100)
    assert len(result) == 100


def test_sanitize_text_dangerous_patterns():
    """Test removal of dangerous patterns."""
    assert _sanitize_text("javascript:alert(1)") == "alert(1)"
    assert _sanitize_text("data:text/html,<script>") == "text/html,"  # <script> removed by HTML filter
    assert _sanitize_text("onclick=alert(1)") == "alert(1)"


def test_user_id_validation():
    """Test user ID validation in database operations."""
    from src.db import upsert_user

    # Should raise for invalid IDs
    with pytest.raises(ValueError):
        import asyncio

        asyncio.run(upsert_user(-1, "test", "test", "test"))

    with pytest.raises(ValueError):
        import asyncio

        asyncio.run(upsert_user(0, "test", "test", "test"))
