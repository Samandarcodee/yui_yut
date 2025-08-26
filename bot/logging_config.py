"""
Logging configuration for the bot
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime
import traceback
from typing import Optional, Dict, Any
import json
import asyncio
from pathlib import Path

class CustomFormatter(logging.Formatter):
    """Custom formatter with colors and structured logging"""
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add custom fields
        record.timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        record.module_short = record.module[:15] if len(record.module) > 15 else record.module
        
        # Colorize the log level
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname_colored = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        
        # Format the message
        if hasattr(record, 'structured_data'):
            # Structured logging
            try:
                data_str = json.dumps(record.structured_data, ensure_ascii=False, indent=2)
                record.msg = f"{record.msg}\n📊 Data: {data_str}"
            except Exception:
                pass
        
        return super().format(record)

class StructuredLogger:
    """Enhanced logger with structured logging capabilities"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        console_formatter = CustomFormatter(
            '%(timestamp)s - %(name)s - %(levelname_colored)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler for all logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "bot.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_formatter.datefmt = '%Y-%m-%d %H:%M:%S'
        file_handler.setFormatter(file_formatter)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        
        # Performance file handler
        perf_handler = logging.handlers.RotatingFileHandler(
            log_dir / "performance.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(file_formatter)
        
        # Add filters
        error_handler.addFilter(lambda record: record.levelno >= logging.ERROR)
        perf_handler.addFilter(lambda record: 'PERFORMANCE' in record.getMessage())
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(perf_handler)
    
    def log_with_data(self, level: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Log message with structured data"""
        if data:
            record = self.logger.makeRecord(
                self.logger.name, getattr(logging, level.upper()), 
                "", 0, message, (), None
            )
            record.structured_data = data
            self.logger.handle(record)
        else:
            getattr(self.logger, level.lower())(message)
    
    def info(self, message: str, data: Optional[Dict[str, Any]] = None):
        self.log_with_data('INFO', message, data)
    
    def warning(self, message: str, data: Optional[Dict[str, Any]] = None):
        self.log_with_data('WARNING', message, data)
    
    def error(self, message: str, data: Optional[Dict[str, Any]] = None, exc_info: bool = True):
        if exc_info:
            data = data or {}
            data['traceback'] = traceback.format_exc()
        self.log_with_data('ERROR', message, data)
    
    def critical(self, message: str, data: Optional[Dict[str, Any]] = None):
        self.log_with_data('CRITICAL', message, data)
    
    def debug(self, message: str, data: Optional[Dict[str, Any]] = None):
        self.log_with_data('DEBUG', message, data)

class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.metrics: Dict[str, Any] = {}
        self.start_times: Dict[str, float] = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.start_times[operation] = asyncio.get_event_loop().time()
    
    def end_timer(self, operation: str, additional_data: Optional[Dict[str, Any]] = None):
        """End timing an operation and log performance"""
        if operation in self.start_times:
            duration = asyncio.get_event_loop().time() - self.start_times[operation]
            
            # Store metric
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration)
            
            # Keep only last 100 measurements
            if len(self.metrics[operation]) > 100:
                self.metrics[operation] = self.metrics[operation][-100:]
            
            # Log performance
            data = {
                'operation': operation,
                'duration_ms': round(duration * 1000, 2),
                'avg_duration_ms': round(sum(self.metrics[operation]) / len(self.metrics[operation]) * 1000, 2),
                'min_duration_ms': round(min(self.metrics[operation]) * 1000, 2),
                'max_duration_ms': round(max(self.metrics[operation]) * 1000, 2),
                'count': len(self.metrics[operation])
            }
            
            if additional_data:
                data.update(additional_data)
            
            self.logger.info(f"PERFORMANCE: {operation} completed in {data['duration_ms']}ms", data)
            
            # Clean up
            del self.start_times[operation]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all operations"""
        summary = {}
        for operation, durations in self.metrics.items():
            if durations:
                summary[operation] = {
                    'avg_ms': round(sum(durations) / len(durations) * 1000, 2),
                    'min_ms': round(min(durations) * 1000, 2),
                    'max_ms': round(max(durations) * 1000, 2),
                    'count': len(durations),
                    'total_time_ms': round(sum(durations) * 1000, 2)
                }
        return summary

class ErrorTracker:
    """Track and analyze errors"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.error_counts: Dict[str, int] = {}
        self.error_contexts: Dict[str, list] = {}
    
    def track_error(self, error_type: str, context: Optional[Dict[str, Any]] = None):
        """Track an error occurrence"""
        # Count errors
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Store context (keep last 10)
        if error_type not in self.error_contexts:
            self.error_contexts[error_type] = []
        
        if context:
            self.error_contexts[error_type].append({
                'timestamp': datetime.now().isoformat(),
                'context': context
            })
            
            # Keep only last 10 contexts
            if len(self.error_contexts[error_type]) > 10:
                self.error_contexts[error_type] = self.error_contexts[error_type][-10:]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary"""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_types': self.error_counts,
            'error_contexts': self.error_contexts
        }
    
    def log_error_summary(self):
        """Log error summary"""
        summary = self.get_error_summary()
        self.logger.info("Error tracking summary", summary)

# Global instances
logger = StructuredLogger("bot.logging_config")
performance_monitor = PerformanceMonitor(logger)
error_tracker = ErrorTracker(logger)

def setup_logging():
    """Setup logging configuration"""
    try:
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Log startup information
        logger.info("=" * 50)
        logger.info("Slot Game Bot Starting Up")
        logger.info(f"Log Level: {logger.logger.level}")
        logger.info(f"Log File: logs/bot.log")
        logger.info(f"Start Time: {datetime.now()}")
        logger.info("=" * 50)
        
        # Log system information
        system_info = {
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': os.getcwd(),
            'log_directory': os.path.abspath("logs")
        }
        logger.info("System information", system_info)
        
        return logger, performance_monitor, error_tracker
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        # Fallback to basic logging
        basic_logger = logging.getLogger("bot")
        basic_logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        basic_logger.addHandler(handler)
        return basic_logger, None, None

def log_exception(logger_instance, message: str, exception: Exception, context: Optional[Dict[str, Any]] = None):
    """Log exception with context"""
    try:
        error_data = {
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'traceback': traceback.format_exc()
        }
        
        if context:
            error_data['context'] = context
        
        logger_instance.error(message, error_data)
        
        # Track error
        if error_tracker:
            error_tracker.track_error(type(exception).__name__, context)
            
    except Exception as e:
        # Fallback logging
        print(f"Failed to log exception: {e}")
        print(f"Original exception: {exception}")

# Performance decorator
def monitor_performance(operation_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            if performance_monitor:
                performance_monitor.start_timer(operation_name)
                try:
                    result = await func(*args, **kwargs)
                    performance_monitor.end_timer(operation_name, {'success': True})
                    return result
                except Exception as e:
                    performance_monitor.end_timer(operation_name, {'success': False, 'error': str(e)})
                    raise
            else:
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            if performance_monitor:
                performance_monitor.start_timer(operation_name)
                try:
                    result = func(*args, **kwargs)
                    performance_monitor.end_timer(operation_name, {'success': True})
                    return result
                except Exception as e:
                    performance_monitor.end_timer(operation_name, {'success': False, 'error': str(e)})
                    raise
            else:
                return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
