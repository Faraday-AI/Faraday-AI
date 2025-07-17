from typing import List, Dict, Optional
from pydantic import BaseModel

class ActivityRecommendationRequest(BaseModel):
    student_id: int
    class_id: int
    preferences: Optional[Dict] = None
    limit: Optional[int] = 5

class ActivityRecommendation(BaseModel):
    activity: Dict
    recommendation_score: float
    score_breakdown: Dict[str, float] 