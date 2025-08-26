"""
🎰 Slot Game Bot — Xavfsizlik va ruxsat berish moduli
"""
import logging
import time
import hashlib
import hmac
import secrets
import re
from typing import Dict, Any, Optional, List, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from collections import defaultdict, deque
import asyncio
from db.database import Database
from config.settings import ADMIN_IDS, CHANNEL_URL, CHANNEL_SUBSCRIPTION_REQUIRED
from keyboards.inline import get_channel_subscription_keyboard

logger = logging.getLogger(__name__)

class SecurityManager:
    """Enhanced security manager with advanced protection features"""
    
    def __init__(self):
        self.rate_limits: Dict[int, deque] = defaultdict(lambda: deque(maxlen=100))
        self.blocked_users: Dict[int, Dict[str, Any]] = {}
        self.suspicious_activities: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self.security_keys: Dict[str, str] = {}
        self.max_requests_per_minute = 60
        self.max_requests_per_hour = 300
        self.suspicious_threshold = 5
        
    def generate_security_key(self, user_id: int) -> str:
        """Generate unique security key for user"""
        timestamp = str(int(time.time()))
        random_part = secrets.token_hex(16)
        key = f"{user_id}_{timestamp}_{random_part}"
        self.security_keys[key] = timestamp
        return key
    
    def verify_security_key(self, key: str, user_id: int, max_age: int = 3600) -> bool:
        """Verify security key validity"""
        if key not in self.security_keys:
            return False
        
        timestamp = int(self.security_keys[key])
        if time.time() - timestamp > max_age:
            del self.security_keys[key]
            return False
        
        # Key is valid, clean up
        del self.security_keys[key]
        return True
    
    def is_rate_limited(self, user_id: int, action: str = "general") -> bool:
        """Enhanced rate limiting with action-specific limits"""
        now = time.time()
        user_limits = self.rate_limits[user_id]
        
        # Clean old entries
        while user_limits and now - user_limits[0] > 3600:  # 1 hour
            user_limits.popleft()
        
        # Check rate limits
        recent_requests = len([t for t in user_limits if now - t < 60])  # Last minute
        hourly_requests = len(user_limits)
        
        if recent_requests > self.max_requests_per_minute:
            self._log_suspicious_activity(user_id, f"Rate limit exceeded: {recent_requests} requests/minute")
            return True
        
        if hourly_requests > self.max_requests_per_hour:
            self._log_suspicious_activity(user_id, f"Hourly limit exceeded: {hourly_requests} requests/hour")
            return True
        
        # Add current request
        user_limits.append(now)
        return False
    
    def _log_suspicious_activity(self, user_id: int, activity: str):
        """Log suspicious activities for monitoring"""
        self.suspicious_activities[user_id].append({
            'timestamp': time.time(),
            'activity': activity,
            'ip': 'unknown'  # Could be enhanced with IP tracking
        })
        
        # Check if user should be flagged
        recent_activities = len([a for a in self.suspicious_activities[user_id] 
                               if time.time() - a['timestamp'] < 3600])
        
        if recent_activities >= self.suspicious_threshold:
            logger.warning(f"User {user_id} flagged for suspicious activity: {recent_activities} incidents")
    
    def block_user(self, user_id: int, reason: str, duration: int = 3600) -> bool:
        """Block user temporarily"""
        try:
            self.blocked_users[user_id] = {
                'reason': reason,
                'blocked_at': time.time(),
                'duration': duration,
                'expires_at': time.time() + duration
            }
            logger.warning(f"User {user_id} blocked: {reason} for {duration} seconds")
            return True
        except Exception as e:
            logger.error(f"Failed to block user {user_id}: {e}")
            return False
    
    def unblock_user(self, user_id: int) -> bool:
        """Unblock user"""
        try:
            if user_id in self.blocked_users:
                del self.blocked_users[user_id]
                logger.info(f"User {user_id} unblocked")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to unblock user {user_id}: {e}")
            return False
    
    def is_user_blocked(self, user_id: int) -> bool:
        """Check if user is blocked"""
        if user_id not in self.blocked_users:
            return False
        
        block_info = self.blocked_users[user_id]
        if time.time() > block_info['expires_at']:
            # Block expired, remove it
            del self.blocked_users[user_id]
            return False
        
        return True
    
    def get_block_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user block information"""
        if user_id not in self.blocked_users:
            return None
        
        block_info = self.blocked_users[user_id].copy()
        block_info['remaining_time'] = max(0, block_info['expires_at'] - time.time())
        return block_info
    
    def validate_payment_amount(self, amount: int) -> bool:
        """Validate payment amount with enhanced checks"""
        try:
            # Basic range check
            if not (50 <= amount <= 10000):
                return False
            
            # Check for suspicious patterns
            if amount % 100 == 0 and amount > 1000:  # Round numbers above 1000
                return False
            
            # Check for common scam amounts
            suspicious_amounts = [999, 1999, 2999, 4999, 9999]
            if amount in suspicious_amounts:
                return False
            
            return True
        except Exception:
            return False
    
    def validate_bonus_amount(self, amount: int) -> bool:
        """Validate bonus amount"""
        try:
            return 0 < amount <= 1000
        except Exception:
            return False
    
    def validate_win_probability(self, probability: float) -> bool:
        """Validate win probability"""
        try:
            return 0.0 <= probability <= 1.0
        except Exception:
            return False
    
    def sanitize_username(self, username: str) -> str:
        """Enhanced username sanitization"""
        if not username:
            return "unknown_user"
        
        # Remove dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}', '[', ']']
        for char in dangerous_chars:
            username = username.replace(char, '')
        
        # Remove non-alphanumeric characters except _ and -
        username = re.sub(r'[^a-zA-Z0-9_-]', '', username)
        
        # Ensure minimum length
        if len(username) < 3:
            username = f"user_{username}"
        
        # Ensure maximum length
        if len(username) > 32:
            username = username[:32]
        
        return username or "unknown_user"
    
    def log_security_event(self, event_type: str, user_id: int, details: str):
        """Enhanced security event logging"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] SECURITY: {event_type} - User {user_id} - {details}"
        
        # Log to file
        logger.warning(log_entry)
        
        # Store in memory for analysis
        self.suspicious_activities[user_id].append({
            'timestamp': time.time(),
            'activity': f"{event_type}: {details}",
            'ip': 'unknown'
        })
    
    def get_security_report(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Generate security report"""
        report = {
            'total_blocked_users': len(self.blocked_users),
            'total_suspicious_users': len(self.suspicious_activities),
            'active_blocks': 0,
            'recent_suspicious_activities': 0
        }
        
        # Count active blocks
        now = time.time()
        for block_info in self.blocked_users.values():
            if now < block_info['expires_at']:
                report['active_blocks'] += 1
        
        # Count recent suspicious activities
        for activities in self.suspicious_activities.values():
            recent = len([a for a in activities if now - a['timestamp'] < 3600])
            report['recent_suspicious_activities'] += recent
        
        if user_id:
            report['user_specific'] = {
                'is_blocked': self.is_user_blocked(user_id),
                'block_info': self.get_block_info(user_id),
                'suspicious_activities': len(self.suspicious_activities.get(user_id, [])),
                'rate_limit_status': len(self.rate_limits.get(user_id, []))
            }
        
        return report
    
    def cleanup_expired_data(self):
        """Clean up expired security data"""
        now = time.time()
        
        # Clean expired blocks
        expired_blocks = [uid for uid, info in self.blocked_users.items() 
                         if now > info['expires_at']]
        for uid in expired_blocks:
            del self.blocked_users[uid]
        
        # Clean old suspicious activities (older than 24 hours)
        for uid in list(self.suspicious_activities.keys()):
            self.suspicious_activities[uid] = [
                a for a in self.suspicious_activities[uid] 
                if now - a['timestamp'] < 86400
            ]
            if not self.suspicious_activities[uid]:
                del self.suspicious_activities[uid]
        
        # Clean old security keys (older than 1 hour)
        expired_keys = [k for k, t in self.security_keys.items() 
                       if now - int(t) > 3600]
        for k in expired_keys:
            del self.security_keys[k]
        
        if expired_blocks or expired_keys:
            logger.info(f"Security cleanup: {len(expired_blocks)} expired blocks, {len(expired_keys)} expired keys")


# Global security manager instance
security_manager = SecurityManager()


class ChannelSubscriptionMiddleware(BaseMiddleware):
    """
    Kanal obunasini majburiy qiluvchi middleware
    Barcha o'yin va funksional xususiyatlar uchun kanal obunasi talab qilinadi
    """
    
    def __init__(self, database: Database):
        super().__init__()
        self.db = database
        
        # Kanal obunasi talab qilinmaydigan handlerlar
        self.exempt_handlers = {
            "start", "verify", "check_subscription", "main_menu",
            "channel_subscription", "back_to_start"
        }
        
        # Kanal obunasi talab qilinmaydigan callback data
        self.exempt_callbacks = {
            "start", "verify", "check_subscription", "main_menu",
            "channel_subscription", "back_to_start"
        }
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Faqat callback query va message larni tekshirish
        if not isinstance(event, (CallbackQuery, Message)):
            return await handler(event, data)
        
        # Foydalanuvchi ID sini olish
        user_id = event.from_user.id if hasattr(event, 'from_user') else None
        if not user_id:
            return await handler(event, data)
        
        # Foydalanuvchi ma'lumotlarini olish
        user = await self.db.get_user(user_id)
        if not user:
            return await handler(event, data)
        
        # Ro'yxatdan o'tmagan foydalanuvchilarni o'tkazib yuborish
        if not user.get('is_verified', False):
            return await handler(event, data)
        
        # Bloklangan foydalanuvchilarni o'tkazib yuborish
        if user.get('is_banned', False):
            return await handler(event, data)
        
        # Kanal obunasini tekshirish
        if not user.get('channel_subscribed', False):
            # Handler nomini aniqlash
            handler_name = handler.__name__ if hasattr(handler, '__name__') else "unknown"
            
            # Callback data ni tekshirish
            if isinstance(event, CallbackQuery):
                callback_data = event.data
                if callback_data in self.exempt_callbacks:
                    return await handler(event, data)
                
                # Kanal obunasi talab qilinadi
                await event.message.edit_text(
                    CHANNEL_SUBSCRIPTION_REQUIRED.format(channel_url=CHANNEL_URL),
                    reply_markup=get_channel_subscription_keyboard(CHANNEL_URL)
                )
                await event.answer("⚠️ Bu funksiyani ishlatish uchun kanal obunasi talab qilinadi!", show_alert=True)
                return
            
            elif isinstance(event, Message):
                # Message uchun ham tekshirish
                if handler_name in self.exempt_handlers:
                    return await handler(event, data)
                
                # Kanal obunasi talab qilinadi
                await event.answer(
                    CHANNEL_SUBSCRIPTION_REQUIRED.format(channel_url=CHANNEL_URL),
                    reply_markup=get_channel_subscription_keyboard(CHANNEL_URL)
                )
                return
        
        # Kanal obunasi mavjud - handler ni davom ettirish
        return await handler(event, data)


class AdminOnlyMiddleware(BaseMiddleware):
    """
    Faqat admin foydalanuvchilar uchun ruxsat beruvchi middleware
    """
    
    def __init__(self, database: Database):
        super().__init__()
        self.db = database
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Faqat callback query va message larni tekshirish
        if not isinstance(event, (CallbackQuery, Message)):
            return await handler(event, data)
        
        # Foydalanuvchi ID sini olish
        user_id = event.from_user.id if hasattr(event, 'from_user') else None
        if not user_id:
            return await handler(event, data)
        
        # Foydalanuvchi ma'lumotlarini olish
        user = await self.db.get_user(user_id)
        if not user:
            return await handler(event, data)
        
        # Admin ekanligini tekshirish
        if user_id not in ADMIN_IDS:
            if isinstance(event, CallbackQuery):
                await event.answer("❌ Bu funksiya faqat adminlar uchun!", show_alert=True)
            else:
                await event.answer("❌ Bu funksiya faqat adminlar uchun!")
            return
        
        # Admin ruxsati mavjud - handler ni davom ettirish
        return await handler(event, data)


# Global middleware instances
channel_subscription_middleware = None
admin_only_middleware = None


async def verify_all_channel_subscriptions(bot, database: Database):
    """
    Barcha foydalanuvchilarning kanal obunasini tekshirish va yangilash
    Bu funksiya muntazam ravishda chaqirilishi kerak
    """
    try:
        # Barcha foydalanuvchilarni olish
        users = await database.get_all_users()
        
        for user in users:
            user_id = user['telegram_id']
            current_status = user.get('channel_subscribed', False)
            
            # Kanal obunasini tekshirish
            is_subscribed = await check_channel_subscription(bot, user_id)
            
            # Status o'zgargan bo'lsa yangilash
            if is_subscribed != current_status:
                await database.set_channel_subscription(user_id, is_subscribed)
                logger.info(f"Foydalanuvchi {user_id} kanal obunasi yangilandi: {current_status} -> {is_subscribed}")
                
                # Agar obuna bekor qilingan bo'lsa, foydalanuvchiga xabar yuborish
                if not is_subscribed and current_status:
                    try:
                        await bot.send_message(
                            user_id,
                            "⚠️ **OGOHLANTIRISH!** ⚠️\n\n"
                            "Siz kanaldan obunani bekor qildingiz!\n\n"
                            "Botning barcha funksiyalarini ishlatish uchun qaytadan obuna bo'lishingiz kerak:\n"
                            f"📢 {CHANNEL_URL}\n\n"
                            "Obuna bo'lgandan so'ng /start buyrug'ini yuboring."
                        )
                    except Exception as e:
                        logger.error(f"Foydalanuvchi {user_id} ga xabar yuborishda xato: {e}")
        
        logger.info("Barcha foydalanuvchilarning kanal obunasi tekshirildi")
        
    except Exception as e:
        logger.error(f"Kanal obunasini tekshirishda xato: {e}")


async def check_channel_subscription(bot, user_id: int) -> bool:
    """
    Foydalanuvchining kanal obunasini tekshirish
    """
    try:
        from config.settings import REQUIRED_CHANNEL
        
        # Kanal a'zosi ekanligini tekshirish
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        
        # Faqat "member", "administrator" yoki "creator" statuslari obuna hisoblanadi
        return member.status in ["member", "administrator", "creator"]
        
    except Exception as e:
        logger.error(f"Foydalanuvchi {user_id} kanal obunasini tekshirishda xato: {e}")
        return False


def setup_middleware(database: Database):
    """Middleware larni sozlash"""
    global channel_subscription_middleware, admin_only_middleware
    
    channel_subscription_middleware = ChannelSubscriptionMiddleware(database)
    admin_only_middleware = AdminOnlyMiddleware(database)
    
    logger.info("Security middleware setup completed")
    
    return channel_subscription_middleware, admin_only_middleware


def rate_limit_check(func):
    """Decorator to check rate limiting"""
    async def wrapper(*args, **kwargs):
        # Extract user_id from different event types
        user_id = None
        
        for arg in args:
            if isinstance(arg, (Message, CallbackQuery)):
                user_id = arg.from_user.id
                break
        
        if user_id and security_manager.is_rate_limited(user_id):
            logger.warning(f"Rate limit exceeded for user {user_id}")
            
            # Send rate limit message if it's a callback query
            for arg in args:
                if isinstance(arg, CallbackQuery):
                    await arg.answer("⚠️ Too many requests. Please slow down.", show_alert=True)
                    return
                elif isinstance(arg, Message):
                    await arg.answer("⚠️ Too many requests. Please wait a moment.")
                    return
        
        return await func(*args, **kwargs)
    
    return wrapper


def admin_required(func):
    """Decorator to require admin privileges"""
    async def wrapper(*args, **kwargs):
        user_id = None
        
        for arg in args:
            if isinstance(arg, (Message, CallbackQuery)):
                user_id = arg.from_user.id
                break
        
        if user_id not in ADMIN_IDS:
            security_manager.log_security_event("UNAUTHORIZED_ADMIN_ACCESS", user_id)
            
            for arg in args:
                if isinstance(arg, CallbackQuery):
                    await arg.answer("❌ Access denied. Admin only.", show_alert=True)
                    return
                elif isinstance(arg, Message):
                    await arg.answer("❌ Access denied. Admin only.")
                    return
        
        return await func(*args, **kwargs)
    
    return wrapper


def validate_user_verified(func):
    """Decorator to ensure user is verified"""
    async def wrapper(*args, **kwargs):
        user_id = None
        
        for arg in args:
            if isinstance(arg, (Message, CallbackQuery)):
                user_id = arg.from_user.id
                break
        
        if user_id:
            db = Database()
            user = await db.get_user(user_id)
            
            if not user or not user.get('is_verified'):
                for arg in args:
                    if isinstance(arg, CallbackQuery):
                        await arg.answer("❌ Please complete registration first!", show_alert=True)
                        return
                    elif isinstance(arg, Message):
                        await arg.answer("❌ Please complete registration first! Use /start")
                        return
        
        return await func(*args, **kwargs)
    
    return wrapper
