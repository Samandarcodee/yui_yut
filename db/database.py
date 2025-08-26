"""
🎰 Slot Game Bot — Yangi ma'lumotlar bazasi moduli (barcha xususiyatlar bilan)
"""
import aiosqlite
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import json
from contextlib import asynccontextmanager
from config.settings import (
    DATABASE_PATH, DEFAULT_WIN_PROBABILITY, DAILY_BONUS_COOLDOWN,
    DAILY_BONUS_AMOUNT, REFERRAL_BONUS, REFERRAL_FRIEND_BONUS
)

logger = logging.getLogger(__name__)


class Database:
    """Optimized database class with connection pooling and query optimization"""
    
    def __init__(self, db_path: str = "data/slot_game.db", max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._connection_pool = asyncio.Queue(maxsize=max_connections)
        self._pool_initialized = False
        
    async def _init_connection_pool(self):
        """Initialize connection pool"""
        if self._pool_initialized:
            return
            
        for _ in range(self.max_connections):
            conn = await aiosqlite.connect(self.db_path)
            await conn.execute("PRAGMA journal_mode=WAL")
            await conn.execute("PRAGMA synchronous=NORMAL")
            await conn.execute("PRAGMA cache_size=10000")
            await conn.execute("PRAGMA temp_store=MEMORY")
            await conn.execute("PRAGMA mmap_size=268435456")
            await conn.execute("PRAGMA optimize")
            self._connection_pool.put_nowait(conn)
        
        self._pool_initialized = True
        logger.info(f"Database connection pool initialized with {self.max_connections} connections")
    
    @asynccontextmanager
    async def _get_connection(self):
        """Get connection from pool with context manager"""
        if not self._pool_initialized:
            await self._init_connection_pool()
            
        conn = await self._connection_pool.get()
        try:
            yield conn
        finally:
            self._connection_pool.put_nowait(conn)
    
    async def init_db(self):
        """Initialize database with optimized schema and indexes"""
        async with self._get_connection() as conn:
            # First, check if we need to migrate existing database
            await self.migrate_database(conn)
            
            # Create tables with optimized structure (only if they don't exist)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    balance INTEGER DEFAULT 100,
                    total_spins INTEGER DEFAULT 0,
                    total_wins INTEGER DEFAULT 0,
                    total_losses INTEGER DEFAULT 0,
                    daily_streak INTEGER DEFAULT 0,
                    last_daily_bonus TIMESTAMP,
                    is_verified BOOLEAN DEFAULT FALSE,
                    is_banned BOOLEAN DEFAULT FALSE,
                    channel_subscribed BOOLEAN DEFAULT FALSE,
                    referral_code TEXT,
                    referred_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS game_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    reels TEXT,
                    is_winner BOOLEAN,
                    stars_won INTEGER,
                    stars_lost INTEGER,
                    win_probability REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id)
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    transaction_type TEXT,
                    amount INTEGER,
                    balance_before INTEGER,
                    balance_after INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (telegram_id)
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert default configuration
            await conn.execute("""
                INSERT OR IGNORE INTO config (key, value) VALUES 
                ('win_probability', '0.7'),
                ('daily_bonus_amount', '5'),
                ('referral_bonus', '10'),
                ('min_payment_amount', '50'),
                ('max_payment_amount', '10000')
            """)
            
            # Create basic indexes only (avoid complex migrations for now)
            try:
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_game_history_user_id ON game_history(user_id)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)")
            except Exception as e:
                logger.warning(f"Index creation failed: {e}")
            
            await conn.commit()
            logger.info("Database initialized successfully")
    
    async def close(self):
        """Close all database connections"""
        if self._pool_initialized:
            while not self._connection_pool.empty():
                conn = await self._connection_pool.get()
                await conn.close()
            self._pool_initialized = False
            logger.info("Database connection pool closed")

    # === FOYDALANUVCHI OPERATSIYALARI ===

    async def register_user(self, telegram_id: int, username: str = None, 
                           first_name: str = None, referrer_id: int = None) -> bool:
        """Yangi foydalanuvchini ro'yxatdan o'tkazish"""
        try:
            async with self._get_connection() as conn:
                await conn.execute("""
                    INSERT OR IGNORE INTO users 
                    (telegram_id, username, first_name, referrer_id, reg_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (telegram_id, username, first_name, referrer_id, datetime.now()))
                await conn.commit()
                
                # Agar referal orqali kelgan bo'lsa
                if referrer_id:
                    await self.add_referral(referrer_id, telegram_id)
                
                return True
        except Exception as e:
            logger.error(f"Foydalanuvchi {telegram_id} ro'yxatdan o'tkazishda xato: {e}")
            return False

    async def verify_user(self, telegram_id: int) -> bool:
        """Foydalanuvchini tasdiqlangan deb belgilash"""
        try:
            async with self._get_connection() as conn:
                await conn.execute("""
                    UPDATE users SET is_verified = 1 WHERE telegram_id = ?
                """, (telegram_id,))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Foydalanuvchi {telegram_id} tasdiqlanishida xato: {e}")
            return False

    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Foydalanuvchi ma'lumotlarini olish - daily streak bilan"""
        try:
            async with self._get_connection() as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.execute("""
                    SELECT * FROM users WHERE telegram_id = ?
                """, (telegram_id,))
                row = await cursor.fetchone()

                if row:
                    user_data = dict(row)

                    # Daily streak hisoblash
                    if user_data.get('last_daily_bonus'):
                        from datetime import datetime, timedelta
                        last_bonus = datetime.fromisoformat(user_data['last_daily_bonus'])
                        today = datetime.now()

                        if (today - last_bonus).days == 1:
                            # Ketma-ket kun
                            user_data['daily_streak'] = user_data.get('daily_streak', 0) + 1
                        elif (today - last_bonus).days > 1:
                            # Ketma-ketlik uzildi
                            user_data['daily_streak'] = 0
                        else:
                            # Bugun bonus olgan
                            user_data['daily_streak'] = user_data.get('daily_streak', 0)
                    else:
                        user_data['daily_streak'] = 0

                    # channel_subscribed maydonini to'g'rilash
                    if 'channel_subscribed' not in user_data:
                        user_data['channel_subscribed'] = False

                    return user_data
                return None
        except Exception as e:
            logger.error(f"Foydalanuvchi {telegram_id} ma'lumotlarini olishda xato: {e}")
            return None

    async def update_user_balance(self, telegram_id: int, stars_delta: int, attempts_delta: int = 0) -> bool:
        """Foydalanuvchi balansini yangilash"""
        try:
            async with self._get_connection() as conn:
                await conn.execute("""
                    UPDATE users 
                    SET stars = MAX(0, stars + ?), attempts = MAX(0, attempts + ?)
                    WHERE telegram_id = ?
                """, (stars_delta, attempts_delta, telegram_id))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Foydalanuvchi {telegram_id} balansi yangilanishida xato: {e}")
            return False

    async def ban_user(self, telegram_id: int) -> bool:
        """Foydalanuvchini bloklash"""
        try:
            async with self._get_connection() as conn:
                await conn.execute("""
                    UPDATE users SET is_banned = 1 WHERE telegram_id = ?
                """, (telegram_id,))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Foydalanuvchi {telegram_id} bloklanishida xato: {e}")
            return False

    async def unban_user(self, telegram_id: int) -> bool:
        """Foydalanuvchini blokdan chiqarish"""
        try:
            async with self._get_connection() as conn:
                await conn.execute("""
                    UPDATE users SET is_banned = 0 WHERE telegram_id = ?
                """, (telegram_id,))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Foydalanuvchi {telegram_id} blokdan chiqarishda xato: {e}")
            return False

    # === O'YIN OPERATSIYALARI ===

    async def record_game_result(self, telegram_id: int, symbols: str, won: bool, stars_won: int = 0) -> bool:
        """O'yin natijasini qayd qilish"""
        try:
            async with self._get_connection() as conn:
                # O'yin tarixiga qo'shish
                await conn.execute("""
                    INSERT INTO game_history (telegram_id, symbols, win_amount, is_win)
                    VALUES (?, ?, ?, ?)
                """, (telegram_id, symbols, stars_won, won))
                
                # Foydalanuvchi statistikasini yangilash
                if won:
                    await conn.execute("""
                        UPDATE users 
                        SET wins = wins + 1, total_spins = total_spins + 1, 
                            stars = stars + ?, attempts = attempts - 1,
                            biggest_win = MAX(biggest_win, ?)
                        WHERE telegram_id = ?
                    """, (stars_won, stars_won, telegram_id))
                else:
                    await conn.execute("""
                        UPDATE users 
                        SET losses = losses + 1, total_spins = total_spins + 1,
                            attempts = attempts - 1
                        WHERE telegram_id = ?
                    """, (telegram_id,))
                
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"O'yin natijasi qayd qilishda xato {telegram_id}: {e}")
            return False

    # === KUNLIK BONUS ===

    async def can_claim_daily_bonus(self, telegram_id: int) -> bool:
        """Kunlik bonusni olish mumkinligini tekshirish"""
        try:
            user = await self.get_user(telegram_id)
            if not user or not user.get('last_daily_bonus'):
                return True
            
            last_bonus = datetime.fromisoformat(user['last_daily_bonus'])
            now = datetime.now()
            
            return (now - last_bonus) >= DAILY_BONUS_COOLDOWN
        except Exception as e:
            logger.error(f"Kunlik bonus tekshirishda xato {telegram_id}: {e}")
            return False

    async def claim_daily_bonus(self, telegram_id: int) -> bool:
        """Kunlik bonusni olish"""
        try:
            if not await self.can_claim_daily_bonus(telegram_id):
                return False
            
            async with self._get_connection() as conn:
                await conn.execute("""
                    UPDATE users 
                    SET stars = stars + ?, last_daily_bonus = ?
                    WHERE telegram_id = ?
                """, (DAILY_BONUS_AMOUNT, datetime.now(), telegram_id))
                
                # Tranzaktsiyani qayd qilish
                await conn.execute("""
                    INSERT INTO transactions 
                    (telegram_id, transaction_type, stars_amount, description)
                    VALUES (?, 'daily_bonus', ?, 'Kunlik bonus')
                """, (telegram_id, DAILY_BONUS_AMOUNT))
                
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Kunlik bonus olishda xato {telegram_id}: {e}")
            return False

    async def get_next_daily_bonus_time(self, telegram_id: int) -> Optional[datetime]:
        """Keyingi kunlik bonus vaqtini olish"""
        try:
            user = await self.get_user(telegram_id)
            if not user or not user.get('last_daily_bonus'):
                return None
            
            last_bonus = datetime.fromisoformat(user['last_daily_bonus'])
            return last_bonus + DAILY_BONUS_COOLDOWN
        except Exception as e:
            logger.error(f"Keyingi bonus vaqti olishda xato {telegram_id}: {e}")
            return None

    # === REFERAL TIZIMI ===

    async def add_referral(self, referrer_id: int, referred_id: int) -> bool:
        """Referal qo'shish"""
        try:
            async with self._get_connection() as conn:
                # Referal jadvliga qo'shish
                await conn.execute("""
                    INSERT INTO referrals (referrer_id, referred_id)
                    VALUES (?, ?)
                """, (referrer_id, referred_id))
                
                # Referrer hisobini yangilash
                await conn.execute("""
                    UPDATE users 
                    SET referral_count = referral_count + 1, stars = stars + ?
                    WHERE telegram_id = ?
                """, (REFERRAL_BONUS, referrer_id))
                
                # Referred foydalanuvchiga ham bonus berish
                await conn.execute("""
                    UPDATE users 
                    SET stars = stars + ?
                    WHERE telegram_id = ?
                """, (REFERRAL_FRIEND_BONUS, referred_id))
                
                # Tranzaktsiyalarni qayd qilish
                await conn.execute("""
                    INSERT INTO transactions 
                    (telegram_id, transaction_type, stars_amount, description)
                    VALUES (?, 'referral_bonus', ?, 'Referal bonusi')
                """, (referrer_id, REFERRAL_BONUS))
                
                await conn.execute("""
                    INSERT INTO transactions 
                    (telegram_id, transaction_type, stars_amount, description)
                    VALUES (?, 'friend_bonus', ?, 'Do''st bonusi')
                """, (referred_id, REFERRAL_FRIEND_BONUS))
                
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Referal qo'shishda xato {referrer_id} -> {referred_id}: {e}")
            return False

    async def get_referral_stats(self, telegram_id: int) -> Dict[str, int]:
        """Referal statistikasini olish"""
        try:
            async with self._get_connection() as conn:
                cursor = await conn.execute("""
                    SELECT referral_count FROM users WHERE telegram_id = ?
                """, (telegram_id,))
                row = await cursor.fetchone()
                
                referral_count = row[0] if row else 0
                total_bonus = referral_count * REFERRAL_BONUS
                
                return {
                    'referrals': referral_count,
                    'total_bonus': total_bonus
                }
        except Exception as e:
            logger.error(f"Referal statistikasi olishda xato {telegram_id}: {e}")
            return {'referrals': 0, 'total_bonus': 0}

    # === STATISTIKALAR ===

    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Eng boy foydalanuvchilar ro'yxati"""
        try:
            async with self._get_connection() as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.execute("""
                    SELECT username, first_name, stars, wins, total_spins, biggest_win
                    FROM users 
                    WHERE is_verified = 1 AND is_banned = 0
                    ORDER BY stars DESC 
                    LIMIT ?
                """, (limit,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Leaderboard olishda xato: {e}")
            return []

    async def get_total_stats(self) -> Dict[str, int]:
        """Umumiy statistikalar"""
        try:
            async with self._get_connection() as conn:
                cursor = await conn.execute("""
                    SELECT 
                        COUNT(*) as total_users,
                        SUM(total_spins) as total_spins,
                        SUM(wins) as total_wins,
                        SUM(losses) as total_losses,
                        SUM(stars) as total_stars,
                        MAX(biggest_win) as biggest_win,
                        COUNT(CASE WHEN is_banned = 1 THEN 1 END) as banned_users
                    FROM users 
                    WHERE is_verified = 1
                """)
                row = await cursor.fetchone()
                return {
                    'total_users': row[0] or 0,
                    'total_spins': row[1] or 0,
                    'total_wins': row[2] or 0,
                    'total_losses': row[3] or 0,
                    'total_stars': row[4] or 0,
                    'biggest_win': row[5] or 0,
                    'banned_users': row[6] or 0
                }
        except Exception as e:
            logger.error(f"Umumiy statistikalar olishda xato: {e}")
            return {}

    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Barcha foydalanuvchilar ro'yxati (admin uchun)"""
        try:
            async with self._get_connection() as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.execute("""
                    SELECT telegram_id, username, first_name, stars, attempts, 
                           total_spins, wins, losses, is_banned, reg_date
                    FROM users 
                    WHERE is_verified = 1
                    ORDER BY reg_date DESC
                """)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Barcha foydalanuvchilar ro'yxatini olishda xato: {e}")
            return []

    # === TRANZAKTSIYALAR ===

    async def add_transaction(self, telegram_id: int, transaction_type: str, 
                           stars_amount: int, attempts_amount: int = 0, 
                           description: str = None) -> bool:
        """Tranzaktsiya qo'shish"""
        try:
            async with self._get_connection() as conn:
                await conn.execute("""
                    INSERT INTO transactions 
                    (telegram_id, transaction_type, stars_amount, attempts_amount, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (telegram_id, transaction_type, stars_amount, attempts_amount, description))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Tranzaktsiya qo'shishda xato: {e}")
            return False

    # === KONFIGURATSIYA ===

    async def get_win_probability(self) -> float:
        """G'alaba ehtimolini olish"""
        try:
            async with self._get_connection() as conn:
                cursor = await conn.execute("SELECT value FROM config WHERE key = 'win_probability'")
                row = await cursor.fetchone()
                return float(row[0]) if row else DEFAULT_WIN_PROBABILITY
        except Exception as e:
            logger.error(f"G'alaba ehtimolini olishda xato: {e}")
            return DEFAULT_WIN_PROBABILITY

    async def set_win_probability(self, probability: float) -> bool:
        """G'alaba ehtimolini o'rnatish"""
        try:
            if not 0.0 <= probability <= 1.0:
                logger.error(f"Noto'g'ri g'alaba ehtimoli: {probability}")
                return False
                
            async with self._get_connection() as conn:
                await conn.execute("""
                    INSERT OR REPLACE INTO config (key, value, updated_at) 
                    VALUES ('win_probability', ?, CURRENT_TIMESTAMP)
                """, (str(probability),))
                await conn.commit()
                logger.info(f"G'alaba ehtimoli yangilandi: {probability}")
                return True
        except Exception as e:
            logger.error(f"G'alaba ehtimolini o'rnatishda xato: {e}")
            return False

    async def get_config_value(self, key: str, default: str = "") -> str:
        """Konfiguratsiya qiymatini olish"""
        try:
            async with self._get_connection() as conn:
                cursor = await conn.execute("SELECT value FROM config WHERE key = ?", (key,))
                row = await cursor.fetchone()
                return row[0] if row else default
        except Exception as e:
            logger.error(f"Konfiguratsiya qiymatini olishda xato: {e}")
            return default

    async def set_config_value(self, key: str, value: str) -> bool:
        """Konfiguratsiya qiymatini o'rnatish"""
        try:
            async with self._get_connection() as conn:
                await conn.execute("""
                    INSERT OR REPLACE INTO config (key, value, updated_at) 
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, value))
                await conn.commit()
                logger.info(f"Konfiguratsiya yangilandi: {key} = {value}")
                return True
        except Exception as e:
            logger.error(f"Konfiguratsiya qiymatini o'rnatishda xato: {e}")
            return False

    async def get_user_statistics(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Foydalanuvchi statistikalarini olish"""
        try:
            async with self._get_connection() as conn:
                conn.row_factory = aiosqlite.Row
                
                # Asosiy ma'lumotlar
                cursor = await conn.execute("""
                    SELECT username, first_name, balance, total_spins, total_wins, total_losses,
                           daily_streak, created_at
                    FROM users WHERE telegram_id = ?
                """, (telegram_id,))
                user_row = await cursor.fetchone()
                
                if not user_row:
                    return None
                
                # O'yin tarixi statistikasi
                cursor = await conn.execute("""
                    SELECT COUNT(*) as total_games,
                           SUM(CASE WHEN is_winner THEN 1 ELSE 0 END) as wins,
                           SUM(CASE WHEN NOT is_winner THEN 1 ELSE 0 END) as losses,
                           SUM(stars_won) as total_stars_won,
                           MAX(stars_won) as biggest_win
                    FROM game_history WHERE user_id = ?
                """, (telegram_id,))
                stats_row = await cursor.fetchone()
                
                # Tranzaktsiya statistikasi
                cursor = await conn.execute("""
                    SELECT COUNT(*) as total_transactions,
                           SUM(CASE WHEN transaction_type = 'purchase' THEN amount ELSE 0 END) as total_purchased,
                           SUM(CASE WHEN transaction_type = 'daily_bonus' THEN amount ELSE 0 END) as total_bonuses
                    FROM transactions WHERE user_id = ?
                """, (telegram_id,))
                trans_row = await cursor.fetchone()
                
                return {
                    **dict(user_row),
                    **dict(stats_row),
                    **dict(trans_row)
                }
                
        except Exception as e:
            logger.error(f"Foydalanuvchi statistikalarini olishda xato: {e}")
            return None

    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Eng yaxshi o'yinchilar ro'yxati"""
        try:
            async with self._get_connection() as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.execute("""
                    SELECT username, first_name, balance, total_wins, total_spins,
                           (CAST(total_wins AS FLOAT) / NULLIF(total_spins, 0) * 100) as win_rate
                    FROM users 
                    WHERE is_verified = 1 AND is_banned = 0 AND total_spins > 0
                    ORDER BY balance DESC, win_rate DESC
                    LIMIT ?
                """, (limit,))
                
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Leaderboard olishda xato: {e}")
            return []

    async def cleanup_old_data(self, days: int = 30) -> bool:
        """Eski ma'lumotlarni tozalash"""
        try:
            async with self._get_connection() as conn:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Eski o'yin tarixini tozalash
                await conn.execute("""
                    DELETE FROM game_history 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                # Eski tranzaktsiyalarni tozalash
                await conn.execute("""
                    DELETE FROM transactions 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                await conn.commit()
                logger.info(f"{days} kundan eski ma'lumotlar tozalandi")
                return True
                
        except Exception as e:
            logger.error(f"Eski ma'lumotlarni tozalashda xato: {e}")
            return False

    async def get_database_stats(self) -> Dict[str, Any]:
        """Ma'lumotlar bazasi statistikasi"""
        try:
            async with self._get_connection() as conn:
                stats = {}
                
                # Foydalanuvchilar statistikasi
                cursor = await conn.execute("""
                    SELECT COUNT(*) as total_users,
                           COUNT(CASE WHEN is_verified = 1 THEN 1 END) as verified_users,
                           COUNT(CASE WHEN is_banned = 1 THEN 1 END) as banned_users,
                           COUNT(CASE WHEN channel_subscribed = 1 THEN 1 END) as subscribed_users
                    FROM users
                """)
                user_stats = await cursor.fetchone()
                stats.update(dict(zip(['total_users', 'verified_users', 'banned_users', 'subscribed_users'], user_stats)))
                
                # O'yin statistikasi
                cursor = await conn.execute("""
                    SELECT COUNT(*) as total_games,
                           SUM(CASE WHEN is_winner THEN 1 ELSE 0 END) as total_wins,
                           AVG(stars_won) as avg_stars_won
                    FROM game_history
                """)
                game_stats = await cursor.fetchone()
                stats.update(dict(zip(['total_games', 'total_wins', 'avg_stars_won'], game_stats)))
                
                # Ma'lumotlar bazasi hajmi
                cursor = await conn.execute("PRAGMA page_count")
                page_count = (await cursor.fetchone())[0]
                cursor = await conn.execute("PRAGMA page_size")
                page_size = (await cursor.fetchone())[0]
                stats['database_size_mb'] = round((page_count * page_size) / (1024 * 1024), 2)
                
                return stats
                
        except Exception as e:
            logger.error(f"Ma'lumotlar bazasi statistikasini olishda xato: {e}")
            return {}

    # === KANAL OBUNASI OPERATSIYALARI ===

    async def set_channel_subscription(self, telegram_id: int, subscribed: bool = True) -> bool:
        """Foydalanuvchining kanal obunasini belgilash"""
        try:
            async with self._get_connection() as conn:
                await conn.execute("""
                    UPDATE users SET channel_subscribed = ? WHERE telegram_id = ?
                """, (subscribed, telegram_id))
                await conn.commit()
                logger.info(f"Foydalanuvchi {telegram_id} kanal obunasi: {subscribed}")
                return True
        except Exception as e:
            logger.error(f"Foydalanuvchi {telegram_id} kanal obunasini belgilashda xato: {e}")
            return False

    async def is_channel_subscribed(self, telegram_id: int) -> bool:
        """Foydalanuvchi kanal obunasi holatini tekshirish"""
        try:
            async with self._get_connection() as conn:
                cursor = await conn.execute("""
                    SELECT channel_subscribed FROM users WHERE telegram_id = ?
                """, (telegram_id,))
                row = await cursor.fetchone()
                
                if row:
                    return bool(row[0])
                return False
        except Exception as e:
            logger.error(f"Foydalanuvchi {telegram_id} kanal obunasini tekshirishda xato: {e}")
            return False

    async def migrate_database(self, db):
        """Database migration - add missing columns and handle schema changes"""
        try:
            # Check if channel_subscribed column exists
            cursor = await db.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in await cursor.fetchall()]
            
            # Add missing columns
            if 'channel_subscribed' not in columns:
                await db.execute("ALTER TABLE users ADD COLUMN channel_subscribed BOOLEAN DEFAULT 0")
                logger.info("Added channel_subscribed column")
            
            if 'daily_streak' not in columns:
                await db.execute("ALTER TABLE users ADD COLUMN daily_streak INTEGER DEFAULT 0")
                logger.info("Added daily_streak column")
            
            # Check config table structure and migrate if needed
            cursor = await db.execute("PRAGMA table_info(config)")
            config_columns = [row[1] for row in await cursor.fetchall()]
            
            if 'key' not in config_columns and 'id' in config_columns:
                # Old schema exists, migrate to new schema
                logger.info("Migrating config table from old to new schema")
                
                # Get existing win_probability value
                cursor = await db.execute("SELECT win_probability FROM config WHERE id = 1")
                row = await cursor.fetchone()
                old_win_probability = row[0] if row else DEFAULT_WIN_PROBABILITY
                
                # Drop old table and create new one
                await db.execute("DROP TABLE config")
                await db.execute("""
                    CREATE TABLE config (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert migrated data
                await db.execute("""
                    INSERT INTO config (key, value) VALUES 
                    ('win_probability', ?),
                    ('daily_bonus_amount', '5'),
                    ('referral_bonus', '10'),
                    ('min_payment_amount', '50'),
                    ('max_payment_amount', '10000')
                """, (str(old_win_probability),))
                
                logger.info("Config table migration completed")
            
            await db.commit()
            logger.info("Database migration completed successfully")
            
        except Exception as e:
            logger.error(f"Database migration error: {e}")
            # Continue even if migration fails
