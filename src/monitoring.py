"""Monitoring and metrics collection for the bot."""
import logging
import time
from typing import Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class BotMetrics:
    """Bot performance and business metrics."""
    start_time: float = field(default_factory=time.time)
    total_spins: int = 0
    total_wins: int = 0
    total_users: int = 0
    total_payments: int = 0
    total_revenue_stars: int = 0
    errors: Dict[str, int] = field(default_factory=dict)
    response_times: list[float] = field(default_factory=list)
    
    def add_spin(self, is_win: bool) -> None:
        """Record a spin result."""
        self.total_spins += 1
        if is_win:
            self.total_wins += 1
    
    def add_payment(self, stars: int) -> None:
        """Record a payment."""
        self.total_payments += 1
        self.total_revenue_stars += stars
    
    def add_error(self, error_type: str) -> None:
        """Record an error."""
        self.errors[error_type] = self.errors.get(error_type, 0) + 1
    
    def add_response_time(self, duration: float) -> None:
        """Record response time."""
        self.response_times.append(duration)
        # Keep only last 1000 measurements
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        uptime = time.time() - self.start_time
        win_rate = (self.total_wins / self.total_spins) if self.total_spins > 0 else 0
        avg_response = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "uptime_seconds": uptime,
            "uptime_hours": uptime / 3600,
            "total_spins": self.total_spins,
            "total_wins": self.total_wins,
            "win_rate": win_rate,
            "total_users": self.total_users,
            "total_payments": self.total_payments,
            "total_revenue_stars": self.total_revenue_stars,
            "avg_response_time_ms": avg_response * 1000,
            "error_count": sum(self.errors.values()),
            "errors_by_type": dict(self.errors),
        }


# Global metrics instance
metrics = BotMetrics()


def log_spin_result(is_win: bool) -> None:
    """Log a spin result for metrics."""
    metrics.add_spin(is_win)


def log_payment(stars: int) -> None:
    """Log a payment for metrics."""
    metrics.add_payment(stars)


def log_error(error_type: str, error: Exception) -> None:
    """Log an error for monitoring."""
    metrics.add_error(error_type)
    logger.error(f"{error_type}: {error}")


def log_response_time(start_time: float) -> None:
    """Log response time for performance monitoring."""
    duration = time.time() - start_time
    metrics.add_response_time(duration)


class PerformanceMiddleware:
    """Middleware to track response times."""
    
    async def __call__(self, handler, event, data):
        start_time = time.time()
        try:
            result = await handler(event, data)
            log_response_time(start_time)
            return result
        except Exception as e:
            log_error("handler_error", e)
            log_response_time(start_time)
            raise
