import pytest
from datetime import datetime, timedelta
import networkx as nx
import numpy as np
from app.main import (
    update_user_streak,
    generate_learning_path,
    get_ai_recommendations,
    get_leaderboard,
    calculate_streak_bonus,
    calculate_tier_bonus,
    get_topic_similarity,
    USER_STREAKS,
    update_leaderboard
)

@pytest.fixture
def mock_user_streak():
    """Fixture for user streak data"""
    streak_data = {
        "current_streak": 10,
        "last_active": datetime.now() - timedelta(hours=23),
        "max_streak": 15,
        "tier": 2,
        "tier_progress": 5,
        "recovery_mode": False,
        "recovery_progress": 0,
        "recovery_multiplier": 1.0,
        "grace_days": 2,
        "grace_used": 0,
        "bonus_points": 100,
        "tier_thresholds": [7, 15, 30, 60],
        "tier_names": ["Bronze", "Silver", "Gold", "Diamond"],
        "activity_history": []
    }
    USER_STREAKS["test_user"] = streak_data
    return streak_data

@pytest.fixture
def mock_user_progress():
    """Fixture for user learning progress"""
    return {
        "Basic Algebra": 0.8,
        "Linear Equations": 0.6,
        "Quadratic Equations": 0.4,
        "Calculus": 0.2
    }

@pytest.fixture
def mock_recent_performance():
    """Fixture for recent performance data"""
    return {
        "Basic Algebra": 0.9,
        "Linear Equations": 0.7,
        "Quadratic Equations": 0.5,
        "Calculus": 0.3
    }

class TestStreakSystem:
    @pytest.mark.asyncio
    async def test_regular_streak_update(self, mock_user_streak):
        """Test regular daily streak update"""
        user_id = "test_user"
        updated = await update_user_streak(user_id)
        
        assert updated["current_streak"] == 11
        assert updated["grace_used"] == 0
        assert updated["tier_progress"] == 6
        assert not updated["recovery_mode"]
        
    @pytest.mark.asyncio
    async def test_grace_period(self, mock_user_streak):
        """Test grace period functionality"""
        mock_user_streak["last_active"] = datetime.now() - timedelta(hours=30)
        user_id = "test_user"
        updated = await update_user_streak(user_id)
        
        assert updated["current_streak"] == 10  # Streak preserved
        assert updated["grace_used"] == 1
        assert updated["recovery_multiplier"] < 1.0
        
    @pytest.mark.asyncio
    async def test_recovery_mode(self, mock_user_streak):
        """Test recovery mode activation"""
        mock_user_streak["last_active"] = datetime.now() - timedelta(days=3)
        user_id = "test_user"
        updated = await update_user_streak(user_id)
        
        assert updated["recovery_mode"]
        assert updated["current_streak"] > 0  # Some progress preserved
        assert updated["tier"] == 1  # Dropped one tier
        
    def test_streak_bonus_calculation(self):
        """Test streak bonus calculations"""
        bonus = calculate_streak_bonus(tier=2, streak=10, multiplier=1.0)
        assert bonus == 200  # Base bonus for tier 2
        
        # Test bonus cap
        large_bonus = calculate_streak_bonus(tier=4, streak=100, multiplier=1.0)
        assert large_bonus == 4000  # Capped at 10x

class TestLearningPath:
    def test_path_generation(self, mock_user_progress):
        """Test learning path generation"""
        path = generate_learning_path(
            current_topic="Basic Algebra",
            user_progress=mock_user_progress
        )
        
        assert len(path) > 0
        assert "Linear Equations" in path
        assert path[0] == "Basic Algebra"
        
    def test_adaptive_difficulty(self, mock_user_progress, mock_recent_performance):
        """Test adaptive difficulty in path generation"""
        path = generate_learning_path(
            current_topic="Basic Algebra",
            user_progress=mock_user_progress,
            recent_performance=mock_recent_performance
        )
        
        # Path should adapt to recent performance
        assert len(path) <= 10  # Max path length check
        assert all(topic in mock_user_progress for topic in path)
        
    def test_topic_similarity(self):
        """Test topic similarity calculation"""
        similarity = get_topic_similarity("Basic Algebra", "Linear Equations")
        assert 0 <= similarity <= 1
        assert similarity > get_topic_similarity("Basic Algebra", "Neural Networks")

class TestAIRecommendations:
    def test_cold_start_recommendations(self):
        """Test recommendations for new users"""
        recs = get_ai_recommendations(user_id=999, n_recommendations=3)
        
        assert isinstance(recs, list)
        assert len(recs) <= 3
        assert all(isinstance(rec, dict) for rec in recs)
        
    def test_personalized_recommendations(self):
        """Test recommendations for existing users"""
        recs = get_ai_recommendations(
            user_id=1,
            topic="Machine Learning",
            n_recommendations=3
        )
        
        assert len(recs) <= 3
        assert all(
            all(key in rec for key in ["title", "url", "difficulty"])
            for rec in recs
        )

class TestLeaderboard:
    @pytest.mark.asyncio
    async def test_leaderboard_sorting(self):
        """Test leaderboard sorting and limits"""
        leaderboard = await get_leaderboard(limit=5)
        
        assert isinstance(leaderboard, list)
        assert len(leaderboard) <= 5
        
        # Check sorting
        if len(leaderboard) > 1:
            scores = [entry["score"] for entry in leaderboard]
            assert scores == sorted(scores, reverse=True)
            
    @pytest.mark.asyncio
    async def test_leaderboard_update(self):
        """Test leaderboard updates with new scores"""
        user_id = "test_user"
        metrics = {
            "accuracy": 0.9,
            "engagement_time": 60,
            "mastery_improvement": 0.2,
            "streak_bonus": 1.5
        }
        
        await update_leaderboard(user_id, metrics)
        leaderboard = await get_leaderboard(limit=10)
        
        assert any(entry["user_id"] == user_id for entry in leaderboard) 
