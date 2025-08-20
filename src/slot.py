import random
from dataclasses import dataclass
from typing import List, Tuple

SYMBOLS = [
    "💎",
    "🔔",
    "🍒",
    "⭐",
    "🍀",
    "🔥",
    "🎲",
]


PAYOUTS = {
    ("💎", "💎", "💎"): 100,
    ("🔔", "🔔", "🔔"): 50,
    ("🍒", "🍒", "🍒"): 25,
    ("⭐", "⭐", "⭐"): 10,
    ("🍀", "🍀", "🍀"): 5,
    ("🔥", "🔥", "🔥"): 3,
    ("🎲", "🎲", "🎲"): 1,
}


@dataclass
class SpinResult:
    reels: Tuple[str, str, str]
    payout: int
    is_win: bool


def _random_reels() -> Tuple[str, str, str]:
    return (
        random.choice(SYMBOLS),
        random.choice(SYMBOLS),
        random.choice(SYMBOLS),
    )


def _compute_payout(reels: Tuple[str, str, str]) -> int:
    # Exact 3-of-a-kind
    if reels in PAYOUTS:
        return PAYOUTS[reels]

    # 2-of-a-kind + 1 different => +1
    a, b, c = reels
    if a == b != c or a == c != b or b == c != a:
        return 1

    # Mixed => 0
    return 0


def spin(with_house_edge: bool = True) -> SpinResult:
    # Uy tomoni uchun ustunlikni ta'minlash maqsadida
    # g'alaba/ mag'lubiyat sinfiga mos kelguncha qayta aralashtirish qilinadi
    target_is_win = random.random() < 0.7 if with_house_edge else None

    for _ in range(50):  # safety cap
        reels = _random_reels()
        payout = _compute_payout(reels)
        is_win = payout > 0
        if target_is_win is None or is_win == target_is_win:
            return SpinResult(reels=reels, payout=payout, is_win=is_win)

    # Fallback: return whatever
    reels = _random_reels()
    payout = _compute_payout(reels)
    return SpinResult(reels=reels, payout=payout, is_win=payout > 0)
