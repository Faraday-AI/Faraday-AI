import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.main import (
    update_user_streak,
    calculate_streak_bonus,
    calculate_tier_bonus,
    USER_STREAKS
)

@pytest.fixture
def invalid_user_streak():
    """Fixture for invalid user streak data"""
    return {
        "current_streak": -1,  # Invalid negative streak
        "last_active": "invalid_date",  # Invalid date format
        "max_streak": "not_a_number",  # Invalid type
        "tier": 5,  # Invalid tier (out of range)
        "tier_progress": -10,  # Invalid negative progress
        "recovery_mode": "not_a_boolean",  # Invalid type
        "recovery_progress": "invalid",  # Invalid type
        "recovery_multiplier": -0.5,  # Invalid negative multiplier
        "grace_days": -1,  # Invalid negative days
        "grace_used": 3,  # Invalid (more than grace_days)
        "bonus_points": "invalid",  # Invalid type
        "tier_thresholds": [],  # Invalid empty thresholds
        "tier_names": None,  # Invalid None value
        "activity_history": None  # Invalid None value
    }

class TestStreakSystemErrors:
    @pytest.mark.asyncio
    async def test_invalid_user_id(self):
        """Test handling of invalid user IDs"""
        invalid_ids = [None, "", " ", "   ", 123, {"id": "user"}, ["user1"]]
        
        for invalid_id in invalid_ids:
            with pytest.raises(ValueError) as exc_info:
                await update_user_streak(invalid_id)
            assert "Invalid user ID" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_nonexistent_user(self):
        """Test handling of nonexistent user streaks"""
        with pytest.raises(HTTPException) as exc_info:
            await update_user_streak("nonexistent_user")
        assert exc_info.value.status_code == 404
        assert "User streak not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_invalid_streak_data(self, invalid_user_streak):
        """Test handling of invalid streak data"""
        user_id = "test_invalid_user"
        USER_STREAKS[user_id] = invalid_user_streak
        
        with pytest.raises(ValueError) as exc_info:
            await update_user_streak(user_id)
        assert "Invalid streak data" in str(exc_info.value)

    def test_streak_bonus_invalid_inputs(self):
        """Test streak bonus calculation with invalid inputs"""
        invalid_cases = [
            (0, 10, 1.0),    # Invalid tier
            (1, -1, 1.0),    # Invalid negative streak
            (1, 10, -0.5),   # Invalid negative multiplier
            (6, 10, 1.0),    # Tier too high
            ("1", 10, 1.0),  # Invalid tier type
            (1, "10", 1.0),  # Invalid streak type
            (1, 10, "1.0")   # Invalid multiplier type
        ]
        
        for tier, streak, multiplier in invalid_cases:
            with pytest.raises((ValueError, TypeError)) as exc_info:
                calculate_streak_bonus(tier, streak, multiplier)
            assert any(msg in str(exc_info.value) for msg in [
                "Invalid tier",
                "Invalid streak",
                "Invalid multiplier"
            ])

    def test_tier_bonus_invalid_inputs(self):
        """Test tier bonus calculation with invalid inputs"""
        invalid_cases = [
            (-1,),      # Negative tier
            (0,),       # Zero tier
            (6,),       # Tier too high
            ("1",),     # Invalid type
            (None,),    # None value
            ([1],),     # Invalid type
            ({1},)      # Invalid type
        ]
        
        for tier, in invalid_cases:
            with pytest.raises((ValueError, TypeError)) as exc_info:
                calculate_tier_bonus(tier)
            assert "Invalid tier" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_concurrent_streak_updates(self):
        """Test handling of concurrent streak updates"""
        user_id = "test_concurrent_user"
        USER_STREAKS[user_id] = {
            "current_streak": 5,
            "last_active": datetime.now() - timedelta(hours=23),
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
        
        # Simulate concurrent updates
        import asyncio
        update_tasks = [update_user_streak(user_id) for _ in range(5)]
        results = await asyncio.gather(*update_tasks, return_exceptions=True)
        
        # Check that only one update succeeded and others failed
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        assert success_count == 1, "Only one concurrent update should succeed"

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting for streak updates"""
        user_id = "test_rate_limit_user"
        USER_STREAKS[user_id] = {
            "current_streak": 1,
            "last_active": datetime.now() - timedelta(minutes=3),  # Definitely within rate limit
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
        
        with pytest.raises(HTTPException) as exc_info:
            await update_user_streak(user_id)
        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in str(exc_info.value.detail) 
