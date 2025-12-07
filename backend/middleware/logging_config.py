"""
Security logging middleware for TradeBerg
Logs security events and suspicious activity
"""
import logging
import json
from datetime import datetime
from fastapi import Request
from typing import Dict, Any
from pathlib import Path


# Create security logger
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# File handler for security logs
security_handler = logging.FileHandler(log_dir / "security.log")
security_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
security_handler.setFormatter(formatter)
security_logger.addHandler(security_handler)


class SecurityLogger:
    """Centralized security logging"""
    
    @staticmethod
    def log_event(
        event_type: str,
        request: Request,
        details: Dict[str, Any] = None,
        level: str = "INFO"
    ):
        """Log security event"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "ip_address": request.client.host if request.client else "unknown",
            "path": request.url.path,
            "method": request.method,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "details": details or {}
        }
        
        log_message = json.dumps(log_data)
        
        if level == "WARNING":
            security_logger.warning(log_message)
        elif level == "ERROR":
            security_logger.error(log_message)
        elif level == "CRITICAL":
            security_logger.critical(log_message)
        else:
            security_logger.info(log_message)
    
    @staticmethod
    def log_failed_login(request: Request, email: str):
        """Log failed login attempt"""
        SecurityLogger.log_event(
            "FAILED_LOGIN",
            request,
            {"email": email},
            "WARNING"
        )
    
    @staticmethod
    def log_rate_limit_exceeded(request: Request):
        """Log rate limit violation"""
        SecurityLogger.log_event(
            "RATE_LIMIT_EXCEEDED",
            request,
            level="WARNING"
        )
    
    @staticmethod
    def log_invalid_input(request: Request, input_type: str):
        """Log invalid input attempt"""
        SecurityLogger.log_event(
            "INVALID_INPUT",
            request,
            {"input_type": input_type},
            "WARNING"
        )
    
    @staticmethod
    def log_suspicious_activity(request: Request, reason: str):
        """Log suspicious activity"""
        SecurityLogger.log_event(
            "SUSPICIOUS_ACTIVITY",
            request,
            {"reason": reason},
            "ERROR"
        )
    
    @staticmethod
    def log_successful_login(request: Request, user_id: str):
        """Log successful login"""
        SecurityLogger.log_event(
            "SUCCESSFUL_LOGIN",
            request,
            {"user_id": user_id},
            "INFO"
        )
