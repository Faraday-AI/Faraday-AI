import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.main import update_user_streak, USER_STREAKS, app
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Fixed time for all tests - must match app.main.py
FIXED_TIME = datetime(2024, 1, 1, 12, 0, 0)

@pytest.fixture(autouse=True)
async def setup_app():
    """Setup FastAPI app state before each test"""
    app.state = type("State", (), {})()
    yield
    # Cleanup after test
    USER_STREAKS.clear()

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting for streak updates"""
    user_id = "test_rate_limit_user"
    last_active = FIXED_TIME - timedelta(minutes=3)  # Less than 5 minutes ago
    
    logger.debug(f"Setting up test with fixed_time: {FIXED_TIME}")
    logger.debug(f"Setting last_active to: {last_active}")
    logger.debug(f"Time difference: {FIXED_TIME - last_active}")
    logger.debug(f"Minutes since last: {(FIXED_TIME - last_active).total_seconds() / 60}")
    
    USER_STREAKS[user_id] = {
        "current_streak": 1,
        "last_active": last_active,  # Using fixed time
        "max_streak": 1,
        "tier": 1,
        "tier_progress": 0,
        "recovery_mode": False,
        "recovery_progress": 0,
        "recovery_multiplier": 1.0,
        "grace_days": 2,
        "grace_used": 0,
        "bonus_points": 0,
        "tier_thresholds": [7, 15, 30, 60],
        "tier_names": ["Bronze", "Silver", "Gold", "Diamond"],
        "activity_history": []
    }
    
    logger.debug(f"Current USER_STREAKS state: {USER_STREAKS[user_id]}")
    
    # Test that rate limiting is enforced
    with pytest.raises(HTTPException) as exc_info:
        await update_user_streak(user_id)
    assert exc_info.value.status_code == 429
    assert "Rate limit exceeded" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_regular_streak_update():
    """Test regular daily streak update"""
    user_id = "test_user"
    last_active = FIXED_TIME - timedelta(hours=25)  # More than 24 hours
    
    logger.debug(f"Setting up test with fixed_time: {FIXED_TIME}")
    logger.debug(f"Setting last_active to: {last_active}")
    logger.debug(f"Time difference: {FIXED_TIME - last_active}")
    logger.debug(f"Hours since last: {(FIXED_TIME - last_active).total_seconds() / 3600}")
    
    USER_STREAKS[user_id] = {
        "current_streak": 10,
        "last_active": last_active,  # Using fixed time
        "max_streak": 10,
        "tier": 1,
        "tier_progress": 0,
        "recovery_mode": False,
        "recovery_progress": 0,
        "recovery_multiplier": 1.0,
        "grace_days": 2,
        "grace_used": 0,
        "bonus_points": 0,
        "tier_thresholds": [7, 15, 30, 60],
        "tier_names": ["Bronze", "Silver", "Gold", "Diamond"],
        "activity_history": []
    }
    
    logger.debug(f"Current USER_STREAKS state: {USER_STREAKS[user_id]}")
    
    updated = await update_user_streak(user_id)
    logger.debug(f"Updated streak data: {updated}")
    assert updated["current_streak"] == 11

@pytest.mark.asyncio
async def test_grace_period():
    """Test grace period functionality"""
    user_id = "test_grace_user"
    last_active = FIXED_TIME - timedelta(hours=36)  # More than 24 but less than 48 hours
    
    logger.debug(f"Setting up test with fixed_time: {FIXED_TIME}")
    logger.debug(f"Setting last_active to: {last_active}")
    logger.debug(f"Time difference: {FIXED_TIME - last_active}")
    logger.debug(f"Hours since last: {(FIXED_TIME - last_active).total_seconds() / 3600}")
    
    USER_STREAKS[user_id] = {
        "current_streak": 5,
        "last_active": last_active,  # Using fixed time
        "max_streak": 5,
        "tier": 1,
        "tier_progress": 0,
        "recovery_mode": False,
        "recovery_progress": 0,
        "recovery_multiplier": 1.0,
        "grace_days": 2,
        "grace_used": 0,
        "bonus_points": 0,
        "tier_thresholds": [7, 15, 30, 60],
        "tier_names": ["Bronze", "Silver", "Gold", "Diamond"],
        "activity_history": []
    }
    
    logger.debug(f"Current USER_STREAKS state: {USER_STREAKS[user_id]}")
    
    updated = await update_user_streak(user_id)
    logger.debug(f"Updated streak data: {updated}")
    assert updated["current_streak"] == 5  # Streak maintained
    assert updated["grace_used"] == 1  # Grace period used
    assert updated["recovery_multiplier"] == 0.9  # Multiplier reduced
