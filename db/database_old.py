"""
🎰 Slot Game Bot — Ma'lumotlar bazasi moduli
"""
import aiosqlite
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from config.settings import DATABASE_PATH, DEFAULT_WIN_PROBABILITY, DAILY_BONUS_COOLDOWN

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Ma'lumotlar bazasini kerakli jadvallar bilan ishga tushirish"""
        async with aiosqlite.connect(self.db_path) as db:
            # Foydalanuvchilar jadvali (yangi maydonlar bilan)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    stars INTEGER DEFAULT 0,
                    attempts INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    total_spins INTEGER DEFAULT 0,
                    biggest_win INTEGER DEFAULT 0,
                    reg_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_daily_bonus DATETIME DEFAULT NULL,
                    referrer_id BIGINT DEFAULT NULL,
                    referral_count INTEGER DEFAULT 0,
                    is_verified BOOLEAN DEFAULT 0,
                    is_banned BOOLEAN DEFAULT 0,
                    FOREIGN KEY (referrer_id) REFERENCES users (telegram_id)
                )
            """)

            # Konfiguratsiya jadvali
            await db.execute(f"""
                CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY,
                    win_probability REAL DEFAULT {DEFAULT_WIN_PROBABILITY}
                )
            """)

            # Standart konfiguratsiyani qo'shish
            await db.execute("""
                INSERT OR IGNORE INTO config (id, win_probability) 
                VALUES (1, ?)
            """, (DEFAULT_WIN_PROBABILITY,))

            # Tranzaktsiyalar jadvali (to'lovlar va bonuslar)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id BIGINT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    stars_amount INTEGER NOT NULL,
                    attempts_amount INTEGER DEFAULT 0,
                    description TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
                )
            """)

            # O'yin tarixi jadvali
            await db.execute("""
                CREATE TABLE IF NOT EXISTS game_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id BIGINT NOT NULL,
                    symbols TEXT NOT NULL,
                    win_amount INTEGER DEFAULT 0,
                    is_win BOOLEAN DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
                )
            """)

            # Referal jadvali
            await db.execute("""
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id BIGINT NOT NULL,
                    referred_id BIGINT NOT NULL,
                    bonus_paid BOOLEAN DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users (telegram_id),
                    FOREIGN KEY (referred_id) REFERENCES users (telegram_id)
                )
            """)

            await db.commit()
            logger.info("Ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi")

    async def register_user(self, telegram_id: int, username: str = None, 
                           first_name: str = None, referrer_id: int = None) -> bool:
        """Yangi foydalanuvchini ro'yxatdan o'tkazish"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR IGNORE INTO users 
                    (telegram_id, username, first_name, referrer_id, reg_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (telegram_id, username, first_name, referrer_id, datetime.now()))
                await db.commit()
                
                # Agar referal orqali kelgan bo'lsa, referal jadvriga qo'shish
                if referrer_id:
                    await self.add_referral(referrer_id, telegram_id)
                
                return True
        except Exception as e:
            logger.error(f"Foydalanuvchi {telegram_id} ro'yxatdan o'tkazishda xato: {e}")
            return False

    async def verify_user(self, telegram_id: int) -> bool:
        """Mark user as verified"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE users SET is_verified = 1 WHERE telegram_id = ?
                """, (telegram_id,))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error verifying user {telegram_id}: {e}")
            return False

    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT * FROM users WHERE telegram_id = ?
                """, (telegram_id,))
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user {telegram_id}: {e}")
            return None

    async def update_user_balance(self, telegram_id: int, stars_delta: int, attempts_delta: int = 0) -> bool:
        """Update user balance and attempts"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE users 
                    SET stars = stars + ?, attempts = attempts + ?
                    WHERE telegram_id = ?
                """, (stars_delta, attempts_delta, telegram_id))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating balance for user {telegram_id}: {e}")
            return False

    async def record_spin_result(self, telegram_id: int, won: bool, stars_won: int = 0) -> bool:
        """Record a spin result"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if won:
                    await db.execute("""
                        UPDATE users 
                        SET wins = wins + 1, total_spins = total_spins + 1, 
                            stars = stars + ?, attempts = attempts - 1
                        WHERE telegram_id = ?
                    """, (stars_won, telegram_id))
                else:
                    await db.execute("""
                        UPDATE users 
                        SET losses = losses + 1, total_spins = total_spins + 1,
                            attempts = attempts - 1
                        WHERE telegram_id = ?
                    """, (telegram_id,))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error recording spin for user {telegram_id}: {e}")
            return False

    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top players by stars"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT username, stars, wins, total_spins
                    FROM users 
                    WHERE is_verified = 1
                    ORDER BY stars DESC 
                    LIMIT ?
                """, (limit,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []

    async def get_total_stats(self) -> Dict[str, int]:
        """Get total statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT 
                        COUNT(*) as total_users,
                        SUM(total_spins) as total_spins,
                        SUM(wins) as total_wins,
                        SUM(losses) as total_losses,
                        SUM(stars) as total_stars
                    FROM users 
                    WHERE is_verified = 1
                """)
                row = await cursor.fetchone()
                return {
                    'total_users': row[0] or 0,
                    'total_spins': row[1] or 0,
                    'total_wins': row[2] or 0,
                    'total_losses': row[3] or 0,
                    'total_stars': row[4] or 0
                }
        except Exception as e:
            logger.error(f"Error getting total stats: {e}")
            return {}

    async def get_win_probability(self) -> float:
        """Get current win probability"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT win_probability FROM config WHERE id = 1")
                row = await cursor.fetchone()
                return row[0] if row else DEFAULT_WIN_PROBABILITY
        except Exception as e:
            logger.error(f"Error getting win probability: {e}")
            return DEFAULT_WIN_PROBABILITY

    async def set_win_probability(self, probability: float) -> bool:
        """Set win probability"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE config SET win_probability = ? WHERE id = 1
                """, (probability,))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error setting win probability: {e}")
            return False

    async def add_transaction(self, telegram_id: int, transaction_type: str, 
                           stars_amount: int, attempts_amount: int = 0) -> bool:
        """Record a transaction"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO transactions 
                    (telegram_id, transaction_type, stars_amount, attempts_amount)
                    VALUES (?, ?, ?, ?)
                """, (telegram_id, transaction_type, stars_amount, attempts_amount))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            return False
