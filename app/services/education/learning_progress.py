from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class ProgressStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MASTERED = "mastered"

class TopicProgress(BaseModel):
    topic_id: str
    status: ProgressStatus
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    score: Optional[float] = None
    attempts: int = 0
    time_spent: int = 0  # in minutes
    notes: Optional[str] = None

class LearningProgress(BaseModel):
    user_id: str
    course_id: str
    topics: Dict[str, TopicProgress] = {}
    overall_progress: float = 0.0
    last_activity: Optional[datetime] = None
    streak_days: int = 0
    total_time_spent: int = 0  # in minutes
    achievements: List[str] = []
    
    def update_topic_progress(
        self,
        topic_id: str,
        status: ProgressStatus,
        score: Optional[float] = None,
        time_spent: Optional[int] = None,
        notes: Optional[str] = None
    ) -> None:
        """Update progress for a specific topic"""
        if topic_id not in self.topics:
            self.topics[topic_id] = TopicProgress(
                topic_id=topic_id,
                status=ProgressStatus.NOT_STARTED
            )
            
        topic = self.topics[topic_id]
        
        if status != topic.status:
            if status == ProgressStatus.IN_PROGRESS and not topic.start_date:
                topic.start_date = datetime.now()
            elif status in [ProgressStatus.COMPLETED, ProgressStatus.MASTERED]:
                topic.completion_date = datetime.now()
        
        topic.status = status
        if score is not None:
            topic.score = score
        if time_spent is not None:
            topic.time_spent += time_spent
            self.total_time_spent += time_spent
        if notes:
            topic.notes = notes
            
        topic.attempts += 1
        self._update_overall_progress()
        self.last_activity = datetime.now()
    
    def _update_overall_progress(self) -> None:
        """Calculate overall progress based on topic statuses"""
        if not self.topics:
            self.overall_progress = 0.0
            return
            
        status_weights = {
            ProgressStatus.NOT_STARTED: 0.0,
            ProgressStatus.IN_PROGRESS: 0.3,
            ProgressStatus.COMPLETED: 0.8,
            ProgressStatus.MASTERED: 1.0
        }
        
        total_weight = sum(status_weights[topic.status] for topic in self.topics.values())
        self.overall_progress = total_weight / len(self.topics)
    
    def update_streak(self) -> None:
        """Update the learning streak"""
        if not self.last_activity:
            self.streak_days = 1
            return
            
        last_date = self.last_activity.date()
        today = datetime.now().date()
        days_diff = (today - last_date).days
        
        if days_diff == 1:  # Consecutive day
            self.streak_days += 1
        elif days_diff > 1:  # Streak broken
            self.streak_days = 1
    
    def add_achievement(self, achievement: str) -> None:
        """Add a new achievement"""
        if achievement not in self.achievements:
            self.achievements.append(achievement)
    
    def get_topic_status(self, topic_id: str) -> ProgressStatus:
        """Get the status of a specific topic"""
        return self.topics.get(topic_id, TopicProgress(topic_id=topic_id, status=ProgressStatus.NOT_STARTED)).status
    
    def get_completed_topics(self) -> List[str]:
        """Get a list of completed topic IDs"""
        return [
            topic_id for topic_id, topic in self.topics.items()
            if topic.status in [ProgressStatus.COMPLETED, ProgressStatus.MASTERED]
        ]
    
    def get_next_topics(self) -> List[str]:
        """Get a list of topic IDs that are not started or in progress"""
        return [
            topic_id for topic_id, topic in self.topics.items()
            if topic.status in [ProgressStatus.NOT_STARTED, ProgressStatus.IN_PROGRESS]
        ] 
