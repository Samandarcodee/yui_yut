"""Tests for slot game mechanics."""

import pytest

from src.slot import PAYOUTS, _compute_payout, spin


def test_payout_calculation():
    """Test payout calculation for different combinations."""
    # Test exact matches
    assert _compute_payout(("💎", "💎", "💎")) == 100
    assert _compute_payout(("🔔", "🔔", "🔔")) == 50
    assert _compute_payout(("🍒", "🍒", "🍒")) == 25

    # Test 2-of-a-kind
    assert _compute_payout(("💎", "💎", "🔔")) == 1
    assert _compute_payout(("🍒", "🔔", "🍒")) == 1

    # Test no match
    assert _compute_payout(("💎", "🔔", "🍒")) == 0


def test_house_edge():
    """Test that game maintains ~50% win rate (fair game)."""
    wins = 0
    total_spins = 1000

    for _ in range(total_spins):
        result = spin(with_house_edge=True)
        if result.is_win:
            wins += 1

    win_rate = wins / total_spins
    # Allow 5% variance for 50/50
    assert 0.45 <= win_rate <= 0.55, f"Win rate {win_rate:.2%} outside expected range"


def test_no_house_edge():
    """Test natural win rate without house edge."""
    wins = 0
    total_spins = 1000

    for _ in range(total_spins):
        result = spin(with_house_edge=False)
        if result.is_win:
            wins += 1

    win_rate = wins / total_spins
    # Natural rate should be different from forced 70%
    print(f"Natural win rate: {win_rate:.2%}")


def test_spin_result_structure():
    """Test SpinResult contains required fields."""
    result = spin()
    assert hasattr(result, "reels")
    assert hasattr(result, "payout")
    assert hasattr(result, "is_win")
    assert len(result.reels) == 3
    assert isinstance(result.payout, int)
    assert isinstance(result.is_win, bool)
