import os
from dataclasses import dataclass
from typing import List
from pathlib import Path

from dotenv import load_dotenv, dotenv_values


# Load .env from project root (parent of src)
_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

_FALLBACK_VALUES = dotenv_values(_ENV_PATH, encoding="utf-8") if _ENV_PATH.exists() else {}


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_ids: List[int]
    channel_username: str | None
    referral_bonus: int
    simulate_donation: bool
    provider_token: str | None
    stars_enabled: bool
    daily_bonus_spins: int
    initial_spins: int  # Yangi foydalanuvchilar uchun boshlang'ich spinlar
    mandatory_channel: str | None  # Majburiy kanal username


def _parse_admin_ids(raw: str | None) -> List[int]:
    if not raw:
        return []
    items = [item.strip() for item in raw.split(",") if item.strip()]
    result: List[int] = []
    for item in items:
        try:
            result.append(int(item))
        except ValueError:
            continue
    return result


def get_settings() -> Settings:
    # Try env first, then fallback parsed values
    token = (os.getenv("BOT_TOKEN") or _FALLBACK_VALUES.get("BOT_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is required in .env")

    admin_ids = _parse_admin_ids(os.getenv("ADMIN_IDS") or _FALLBACK_VALUES.get("ADMIN_IDS"))
    channel_username = os.getenv("CHANNEL_USERNAME") or _FALLBACK_VALUES.get("CHANNEL_USERNAME")
    referral_bonus = int(os.getenv("REFERRAL_BONUS") or _FALLBACK_VALUES.get("REFERRAL_BONUS") or "5")
    simulate_donation = (os.getenv("SIMULATE_DONATION") or _FALLBACK_VALUES.get("SIMULATE_DONATION") or "true").lower() in {"1", "true", "yes"}
    provider_token = ((os.getenv("PROVIDER_TOKEN") or _FALLBACK_VALUES.get("PROVIDER_TOKEN") or "").strip() or None)
    stars_enabled = (os.getenv("STARS_ENABLED") or _FALLBACK_VALUES.get("STARS_ENABLED") or "true").lower() in {"1", "true", "yes"}
    daily_bonus_spins = int(os.getenv("DAILY_BONUS_SPINS") or _FALLBACK_VALUES.get("DAILY_BONUS_SPINS") or "5")
    initial_spins = int(os.getenv("INITIAL_SPINS") or _FALLBACK_VALUES.get("INITIAL_SPINS") or "10")
    mandatory_channel = os.getenv("MANDATORY_CHANNEL") or _FALLBACK_VALUES.get("MANDATORY_CHANNEL")

    return Settings(
        bot_token=token,
        admin_ids=admin_ids,
        channel_username=channel_username,
        referral_bonus=referral_bonus,
        simulate_donation=simulate_donation,
        provider_token=provider_token,
        stars_enabled=stars_enabled,
        daily_bonus_spins=daily_bonus_spins,
        initial_spins=initial_spins,
        mandatory_channel=mandatory_channel,
    )


