"""
Rate limiting and quota management for AI API calls.
Handles Google Gemini API quota limits and provides graceful fallbacks.
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Callable
from functools import wraps
import os

logger = logging.getLogger(__name__)

class APIRateLimiter:
    """
    Manages API rate limiting and quota tracking for Google Gemini API.
    Provides graceful degradation when limits are exceeded.
    """
    
    def __init__(self, quota_file: str = "api_quota.json"):
        self.quota_file = os.path.join(os.path.dirname(__file__), quota_file)
        self.daily_limit = 50  # Free tier limit
        self.reset_hour = 0  # UTC midnight
        self.load_quota_data()
        
    def load_quota_data(self):
        """Load quota usage data from file."""
        try:
            if os.path.exists(self.quota_file):
                with open(self.quota_file, 'r') as f:
                    data = json.load(f)
                    self.usage_count = data.get('usage_count', 0)
                    self.last_reset = datetime.fromisoformat(data.get('last_reset', datetime.now().isoformat()))
            else:
                self.usage_count = 0
                self.last_reset = datetime.now()
                self.save_quota_data()
        except Exception as e:
            logger.error(f"Error loading quota data: {e}")
            self.usage_count = 0
            self.last_reset = datetime.now()
    
    def save_quota_data(self):
        """Save quota usage data to file."""
        try:
            data = {
                'usage_count': self.usage_count,
                'last_reset': self.last_reset.isoformat(),
                'daily_limit': self.daily_limit
            }
            with open(self.quota_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving quota data: {e}")
    
    def should_reset_quota(self) -> bool:
        """Check if quota should be reset (new day)."""
        now = datetime.now()
        return (now.date() > self.last_reset.date() or 
                (now.date() == self.last_reset.date() and 
                 now.hour >= self.reset_hour and 
                 self.last_reset.hour < self.reset_hour))
    
    def reset_quota_if_needed(self):
        """Reset quota if a new day has started."""
        if self.should_reset_quota():
            self.usage_count = 0
            self.last_reset = datetime.now()
            self.save_quota_data()
            logger.info("API quota reset for new day")
    
    def can_make_request(self) -> bool:
        """Check if we can make an API request."""
        self.reset_quota_if_needed()
        return self.usage_count < self.daily_limit
    
    def record_request(self):
        """Record an API request."""
        self.usage_count += 1
        self.save_quota_data()
        logger.info(f"API request recorded. Usage: {self.usage_count}/{self.daily_limit}")
    
    def get_quota_status(self) -> Dict[str, Any]:
        """Get current quota status."""
        self.reset_quota_if_needed()
        remaining = max(0, self.daily_limit - self.usage_count)
        next_reset = datetime.now().replace(hour=self.reset_hour, minute=0, second=0, microsecond=0)
        if next_reset <= datetime.now():
            next_reset += timedelta(days=1)
        
        return {
            'used': self.usage_count,
            'limit': self.daily_limit,
            'remaining': remaining,
            'next_reset': next_reset.isoformat(),
            'can_make_request': self.can_make_request()
        }

# Global rate limiter instance
rate_limiter = APIRateLimiter()

def with_rate_limit(fallback_function: Optional[Callable] = None):
    """
    Decorator to add rate limiting to API functions.
    
    Args:
        fallback_function: Function to call when rate limit is exceeded
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not rate_limiter.can_make_request():
                logger.warning(f"API rate limit exceeded. Using fallback for {func.__name__}")
                if fallback_function:
                    return fallback_function(*args, **kwargs)
                else:
                    return {
                        "suggestion": "Rate limit exceeded. Please try again later.",
                        "confidence": "low",
                        "method": "rate_limited",
                        "error": "quota_exceeded",
                        "quota_status": rate_limiter.get_quota_status()
                    }
            
            try:
                rate_limiter.record_request()
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                error_str = str(e)
                if "ResourceExhausted" in error_str or "429" in error_str or "quota" in error_str.lower():
                    logger.error(f"API quota exceeded: {e}")
                    # Force quota to max to prevent further requests
                    rate_limiter.usage_count = rate_limiter.daily_limit
                    rate_limiter.save_quota_data()
                    
                    if fallback_function:
                        return fallback_function(*args, **kwargs)
                    else:
                        return {
                            "suggestion": "API quota exceeded. Please try again tomorrow.",
                            "confidence": "low", 
                            "method": "quota_exceeded",
                            "error": "quota_exceeded",
                            "quota_status": rate_limiter.get_quota_status()
                        }
                else:
                    logger.error(f"API error in {func.__name__}: {e}")
                    raise
                    
        return wrapper
    return decorator

def get_quota_status() -> Dict[str, Any]:
    """Get current API quota status."""
    return rate_limiter.get_quota_status()

def reset_quota():
    """Manually reset quota (for testing or admin purposes)."""
    rate_limiter.usage_count = 0
    rate_limiter.last_reset = datetime.now()
    rate_limiter.save_quota_data()
    logger.info("API quota manually reset")
