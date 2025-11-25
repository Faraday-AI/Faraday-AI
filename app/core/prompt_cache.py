"""
Prompt and Intent Caching Layer
Reduces token usage and improves response time by caching frequently accessed data.
"""

import hashlib
import logging
from typing import Optional, Dict, Tuple
from functools import lru_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# In-memory cache (can be upgraded to Redis later)
_intent_cache: Dict[str, Tuple[str, datetime]] = {}
_prompt_cache: Dict[str, Tuple[str, datetime]] = {}
_metadata_cache: Dict[str, Tuple[Dict, datetime]] = {}

# Cache TTL (time to live)
INTENT_CACHE_TTL = timedelta(minutes=5)
PROMPT_CACHE_TTL = timedelta(hours=1)
METADATA_CACHE_TTL = timedelta(minutes=10)


def _cache_key(text: str, prefix: str = "") -> str:
    """Generate cache key from text."""
    key = f"{prefix}:{text.lower().strip()}"
    return hashlib.md5(key.encode()).hexdigest()


def get_cached_intent(user_message: str) -> Optional[str]:
    """
    Get cached intent classification result.
    
    Args:
        user_message: User's message
        
    Returns:
        Cached intent or None if not found/expired
    """
    cache_key = _cache_key(user_message, "intent")
    
    if cache_key in _intent_cache:
        intent, cached_time = _intent_cache[cache_key]
        if datetime.now() - cached_time < INTENT_CACHE_TTL:
            logger.debug(f"✅ Cache hit for intent: {intent}")
            return intent
        else:
            # Expired, remove from cache
            del _intent_cache[cache_key]
    
    return None


def cache_intent(user_message: str, intent: str):
    """Cache intent classification result."""
    cache_key = _cache_key(user_message, "intent")
    _intent_cache[cache_key] = (intent, datetime.now())
    logger.debug(f"💾 Cached intent: {intent} for message: {user_message[:50]}...")


def get_cached_prompt(prompt_key: str) -> Optional[str]:
    """
    Get cached prompt content.
    
    Args:
        prompt_key: Key identifying the prompt (e.g., "root", "meal_plan")
        
    Returns:
        Cached prompt content or None if not found/expired
    """
    if prompt_key in _prompt_cache:
        content, cached_time = _prompt_cache[prompt_key]
        if datetime.now() - cached_time < PROMPT_CACHE_TTL:
            logger.debug(f"✅ Cache hit for prompt: {prompt_key}")
            return content
        else:
            # Expired, remove from cache
            del _prompt_cache[prompt_key]
    
    return None


def cache_prompt(prompt_key: str, content: str):
    """Cache prompt content."""
    _prompt_cache[prompt_key] = (content, datetime.now())
    logger.debug(f"💾 Cached prompt: {prompt_key} ({len(content)} chars)")


def get_cached_metadata(metadata_key: str) -> Optional[Dict]:
    """
    Get cached metadata (teacher profiles, student data, etc.).
    
    Args:
        metadata_key: Key identifying the metadata
        
    Returns:
        Cached metadata dict or None if not found/expired
    """
    if metadata_key in _metadata_cache:
        data, cached_time = _metadata_cache[metadata_key]
        if datetime.now() - cached_time < METADATA_CACHE_TTL:
            logger.debug(f"✅ Cache hit for metadata: {metadata_key}")
            return data
        else:
            # Expired, remove from cache
            del _metadata_cache[metadata_key]
    
    return None


def cache_metadata(metadata_key: str, data: Dict):
    """Cache metadata."""
    _metadata_cache[metadata_key] = (data, datetime.now())
    logger.debug(f"💾 Cached metadata: {metadata_key}")


def clear_cache():
    """Clear all caches (useful for testing or memory management)."""
    global _intent_cache, _prompt_cache, _metadata_cache
    _intent_cache.clear()
    _prompt_cache.clear()
    _metadata_cache.clear()
    logger.info("🗑️ Cleared all caches")


def get_cache_stats() -> Dict[str, int]:
    """Get cache statistics."""
    return {
        "intent_cache_size": len(_intent_cache),
        "prompt_cache_size": len(_prompt_cache),
        "metadata_cache_size": len(_metadata_cache)
    }

