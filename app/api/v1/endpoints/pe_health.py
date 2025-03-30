from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.lesson import User
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

router = APIRouter()

class HealthCheckResponse(BaseModel):
    status: str
    details: Dict[str, Any]

@router.get("/health", response_model=HealthCheckResponse)
async def check_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check the health status of the PE service."""
    try:
        # Add any specific health checks here
        return {
            "status": "healthy",
            "details": {
                "service": "physical_education",
                "status": "operational",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        ) 