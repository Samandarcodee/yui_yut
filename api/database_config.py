"""
Database configuration for Vercel deployment
"""
import os
import aiosqlite
from pathlib import Path

# Vercel environment uchun database path
def get_database_path():
    """Get database path for Vercel"""
    if os.getenv('VERCEL'):
        # Vercel production
        return '/tmp/slot_game.db'
    else:
        # Local development
        return 'data/slot_game.db'

# Database connection for Vercel
async def get_vercel_db():
    """Get database connection optimized for Vercel"""
    db_path = get_database_path()
    
    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = await aiosqlite.connect(db_path)
    
    # Optimize for Vercel
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA synchronous=NORMAL")
    await conn.execute("PRAGMA cache_size=1000")
    await conn.execute("PRAGMA temp_store=MEMORY")
    
    return conn

# Initialize database for Vercel
async def init_vercel_db():
    """Initialize database with basic schema for Vercel"""
    conn = await get_vercel_db()
    
    try:
        # Create basic tables
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                balance INTEGER DEFAULT 100,
                total_spins INTEGER DEFAULT 0,
                total_wins INTEGER DEFAULT 0,
                total_losses INTEGER DEFAULT 0,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                reels TEXT,
                is_winner BOOLEAN,
                stars_won INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        """)
        
        await conn.commit()
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False
    
    finally:
        await conn.close()
