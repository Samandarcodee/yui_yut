"""Database operations with SQLite and security measures."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import aiosqlite

logger = logging.getLogger(__name__)

DB_PATH = "uyin.sqlite3"


CREATE_USERS_SQL = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    stars INTEGER NOT NULL DEFAULT 0,
    spins INTEGER NOT NULL DEFAULT 0,
    biggest_win INTEGER NOT NULL DEFAULT 0,
    referred_by INTEGER,
    is_banned INTEGER NOT NULL DEFAULT 0,
    free_play INTEGER NOT NULL DEFAULT 0,
    vip_level INTEGER NOT NULL DEFAULT 0,
    utm_source TEXT,
    utm_campaign TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


CREATE_INDEXES_SQL = """
CREATE INDEX IF NOT EXISTS idx_users_stars ON users(stars DESC);
CREATE INDEX IF NOT EXISTS idx_users_spins ON users(spins DESC);
"""


CREATE_STATS_SQL = """
CREATE TABLE IF NOT EXISTS user_stats (
    user_id INTEGER PRIMARY KEY,
    total_spins INTEGER NOT NULL DEFAULT 0,
    total_wins INTEGER NOT NULL DEFAULT 0,
    total_stars_won INTEGER NOT NULL DEFAULT 0,
    last_played_at TIMESTAMP
);
"""


CREATE_SPINS_LOG_SQL = """
CREATE TABLE IF NOT EXISTS spins_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    r1 TEXT NOT NULL,
    r2 TEXT NOT NULL,
    r3 TEXT NOT NULL,
    payout INTEGER NOT NULL,
    is_win INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_spins_user ON spins_log(user_id DESC, created_at DESC);
"""


CREATE_PAYMENTS_SQL = """
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    kind TEXT NOT NULL, -- stars_invoice | referral_bonus | admin_grant
    stars INTEGER NOT NULL DEFAULT 0,
    spins_added INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id DESC, created_at DESC);
"""


CREATE_DAILY_BONUS_SQL = """
CREATE TABLE IF NOT EXISTS daily_bonus (
    user_id INTEGER PRIMARY KEY,
    last_claim_date TEXT
);
"""


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        # executescript allows multiple statements at once
        await db.executescript(
            CREATE_USERS_SQL
            + "\n"
            + CREATE_INDEXES_SQL
            + "\n"
            + CREATE_STATS_SQL
            + "\n"
            + CREATE_SPINS_LOG_SQL
            + "\n"
            + CREATE_PAYMENTS_SQL
            + "\n"
            + CREATE_DAILY_BONUS_SQL
        )
        await db.commit()
        # Lightweight migration for added columns if existing DB
        await _migrate_users_table(db)


async def upsert_user(
    user_id: int,
    username: Optional[str],
    first_name: Optional[str],
    last_name: Optional[str],
    referred_by: Optional[int] = None,
    initial_spins: int = 0,
) -> None:
    """Securely insert or update user with input validation."""
    if user_id <= 0:
        raise ValueError("Invalid user_id")

    # Sanitize string inputs
    username = (username or "").strip()[:50] if username else None
    first_name = (first_name or "").strip()[:100] if first_name else None
    last_name = (last_name or "").strip()[:100] if last_name else None

    # Validate referred_by
    if referred_by is not None and (referred_by <= 0 or referred_by == user_id):
        referred_by = None

    # Validate initial_spins
    initial_spins = max(0, min(initial_spins, 1000))  # Cap at 1000

    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Use parameterized queries to prevent SQL injection
            await db.execute(
                """
                INSERT INTO users(user_id, username, first_name, last_name, referred_by, spins)
                VALUES(?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username=excluded.username,
                    first_name=excluded.first_name,
                    last_name=excluded.last_name
                """,
                (user_id, username, first_name, last_name, referred_by, initial_spins),
            )
            await db.commit()
            logger.debug(f"User {user_id} upserted successfully")
    except Exception as e:
        logger.error(f"Failed to upsert user {user_id}: {e}")
        raise


async def _migrate_users_table(db: aiosqlite.Connection) -> None:
    # Add missing columns if DB was created earlier
    await db.execute("PRAGMA foreign_keys=OFF;")
    cols: list[str] = []
    async with db.execute("PRAGMA table_info(users)") as cur:
        async for row in cur:
            cols.append(row[1])  # name

    async def add(col: str, ddl: str) -> None:
        if col not in cols:
            try:
                await db.execute(f"ALTER TABLE users ADD COLUMN {ddl}")
            except Exception:
                pass

    await add("is_banned", "is_banned INTEGER NOT NULL DEFAULT 0")
    await add("free_play", "free_play INTEGER NOT NULL DEFAULT 0")
    await add("vip_level", "vip_level INTEGER NOT NULL DEFAULT 0")
    await add("utm_source", "utm_source TEXT")
    await add("utm_campaign", "utm_campaign TEXT")
    await db.commit()


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            if row is None:
                return None
            return dict(row)


async def add_spins(user_id: int, amount: int) -> None:
    """Add spins to user account with validation and logging."""
    if amount == 0:
        return
    
    # Validate inputs
    if user_id <= 0:
        raise ValueError("Invalid user_id")
    if abs(amount) > 10000:  # Prevent extreme values
        raise ValueError("Amount too large")
    
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Use MAX to prevent negative spins
            await db.execute(
                "UPDATE users SET spins = MAX(spins + ?, 0) WHERE user_id=?", 
                (amount, user_id)
            )
            await db.commit()
            logger.debug(f"Added {amount} spins to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to add spins to user {user_id}: {e}")
        raise


async def add_stars(user_id: int, amount: int) -> None:
    """Add stars to user account with validation and logging."""
    if amount == 0:
        return
    
    # Validate inputs
    if user_id <= 0:
        raise ValueError("Invalid user_id")
    if abs(amount) > 100000:  # Prevent extreme values
        raise ValueError("Amount too large")
    
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Use MAX to prevent negative stars
            await db.execute(
                "UPDATE users SET stars = MAX(stars + ?, 0) WHERE user_id=?", 
                (amount, user_id)
            )
            await db.commit()
            logger.debug(f"Added {amount} stars to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to add stars to user {user_id}: {e}")
        raise


async def set_biggest_win_if_greater(user_id: int, value: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET biggest_win = CASE WHEN ? > biggest_win THEN ? ELSE biggest_win END WHERE user_id=?",
            (value, value, user_id),
        )
        await db.commit()


async def get_top_by_stars(limit: int = 10) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY stars DESC LIMIT ?", (limit,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


async def increment_referrer_stars(referrer_id: int, bonus: int) -> None:
    await add_stars(referrer_id, bonus)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO payments(user_id, kind, stars, spins_added) VALUES(?, 'referral_bonus', ?, 0)",
            (referrer_id, bonus),
        )
        await db.commit()


async def increment_level2_referrer_stars(second_level_referrer_id: int, bonus: int) -> None:
    await add_stars(second_level_referrer_id, bonus)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO payments(user_id, kind, stars, spins_added) VALUES(?, 'referral_level2', ?, 0)",
            (second_level_referrer_id, bonus),
        )
        await db.commit()


async def record_spin(user_id: int, reels: Tuple[str, str, str], payout: int, is_win: bool) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO spins_log(user_id, r1, r2, r3, payout, is_win) VALUES(?, ?, ?, ?, ?, ?)",
            (user_id, reels[0], reels[1], reels[2], payout, 1 if is_win else 0),
        )
        await db.execute(
            """
            INSERT INTO user_stats(user_id, total_spins, total_wins, total_stars_won, last_played_at)
            VALUES(?, 1, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                total_spins = user_stats.total_spins + 1,
                total_wins = user_stats.total_wins + excluded.total_wins,
                total_stars_won = user_stats.total_stars_won + excluded.total_stars_won,
                last_played_at = CURRENT_TIMESTAMP
            """,
            (user_id, 1 if is_win else 0, payout if is_win else 0),
        )
        await db.commit()


async def log_payment(user_id: int, kind: str, stars: int, spins_added: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO payments(user_id, kind, stars, spins_added) VALUES(?, ?, ?, ?)",
            (user_id, kind, stars, spins_added),
        )
        await db.commit()


async def get_user_with_stats(user_id: int) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT u.*, s.total_spins, s.total_wins, s.total_stars_won, s.last_played_at
            FROM users u
            LEFT JOIN user_stats s ON s.user_id = u.user_id
            WHERE u.user_id = ?
            """,
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def count_invited(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users WHERE referred_by=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return int(row[0]) if row else 0


async def can_claim_daily_bonus(user_id: int, today: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT last_claim_date FROM daily_bonus WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                return True
            return row[0] != today


async def set_daily_claimed(user_id: int, today: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO daily_bonus(user_id, last_claim_date)
            VALUES(?, ?)
            ON CONFLICT(user_id) DO UPDATE SET last_claim_date=excluded.last_claim_date
            """,
            (user_id, today),
        )
        await db.commit()


async def get_recent_spins(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM spins_log WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


async def update_user_utm(user_id: int, source: Optional[str], campaign: Optional[str]) -> None:
    if not source and not campaign:
        return
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET utm_source=COALESCE(?, utm_source), utm_campaign=COALESCE(?, utm_campaign) WHERE user_id=?",
            (source, campaign, user_id),
        )
        await db.commit()


# Admin utilities
async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE lower(username)=lower(?)", (username,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def set_ban(user_id: int, banned: bool) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_banned=? WHERE user_id=?", (1 if banned else 0, user_id))
        await db.commit()


async def set_free_play(user_id: int, free_play: bool) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET free_play=? WHERE user_id=?", (1 if free_play else 0, user_id))
        await db.commit()


async def set_vip_level(user_id: int, level: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET vip_level=? WHERE user_id=?", (level, user_id))
        await db.commit()


async def get_active_user_ids(days: int) -> List[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT DISTINCT user_id FROM spins_log WHERE created_at >= datetime('now', ?)",
            (f"-{days} days",),
        ) as cur:
            rows = await cur.fetchall()
            return [int(r[0]) for r in rows]


async def get_vip_user_ids() -> List[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users WHERE vip_level > 0") as cur:
            rows = await cur.fetchall()
            return [int(r[0]) for r in rows]


async def compute_kpis() -> Dict[str, Any]:
    async with aiosqlite.connect(DB_PATH) as db:
        out: Dict[str, Any] = {}
        # DAU/WAU/MAU
        for k, days in (("dau", 1), ("wau", 7), ("mau", 30)):
            async with db.execute(
                "SELECT COUNT(DISTINCT user_id) FROM spins_log WHERE created_at >= datetime('now', ?)",
                (f"-{days} days",),
            ) as cur:
                row = await cur.fetchone()
                out[k] = int(row[0]) if row and row[0] is not None else 0
        # Users count
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            row = await cur.fetchone()
            total_users = int(row[0]) if row else 0
        out["users"] = total_users
        # Conversion, ARPU
        async with db.execute(
            "SELECT COUNT(DISTINCT user_id), COALESCE(SUM(stars),0) FROM payments WHERE kind='stars_invoice'"
        ) as cur:
            row = await cur.fetchone()
            payers = int(row[0]) if row else 0
            revenue = int(row[1]) if row else 0
        out["payers"] = payers
        out["revenue_stars"] = revenue
        out["conversion"] = (payers / total_users) if total_users else 0.0
        out["arpu_stars"] = (revenue / total_users) if total_users else 0.0
        return out
