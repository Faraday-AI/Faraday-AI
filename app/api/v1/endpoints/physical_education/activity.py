from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.services.physical_education.recommendation_engine import RecommendationEngine
from app.api.v1.models.activity import ActivityRecommendationRequest, ActivityRecommendation

router = APIRouter()

@router.post("/recommendations", response_model=List[ActivityRecommendation])
async def get_activity_recommendations(
    request: ActivityRecommendationRequest,
    db: Session = Depends(get_db)
):
    """Get personalized activity recommendations for a student."""
    try:
        recommendation_engine = RecommendationEngine(db)
        recommendations = recommendation_engine.get_activity_recommendations(
            student_id=request.student_id,
            class_id=request.class_id,
            preferences=request.preferences,
            limit=request.limit
        )
        return recommendations
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}") 