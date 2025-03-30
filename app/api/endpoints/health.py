from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.core.monitoring import system_monitor, model_monitor
from app.services.ai_analytics import AIAnalytics
from app.services.ai_analytics import get_ai_analytics_service

router = APIRouter()

@router.get("/health")
async def health_check(
    ai_analytics: AIAnalytics = Depends(get_ai_analytics_service)
) -> Dict[str, Any]:
    """Get system health status."""
    try:
        # Get system metrics
        system_health = system_monitor.get_system_health()
        
        # Get model metrics
        model_metrics = model_monitor.get_model_metrics()
        
        # Check model availability
        model_status = {
            "performance_model": ai_analytics.performance_model is not None,
            "behavior_model": ai_analytics.behavior_model is not None,
            "audio_model": ai_analytics.audio_model is not None,
            "vision_models": {
                "pose": ai_analytics.pose is not None,
                "face_mesh": ai_analytics.face_mesh is not None
            }
        }
        
        # Check API key
        api_key_status = bool(ai_analytics.openai_client.api_key)
        
        # Determine overall status
        all_models_available = all(model_status.values())
        system_healthy = (
            system_health.get("cpu_usage", 100) < 90 and
            system_health.get("memory_usage", float('inf')) < 0.9 * 1024**3  # 90% of 1GB
        )
        
        status = "healthy" if all_models_available and system_healthy and api_key_status else "degraded"
        
        return {
            "status": status,
            "system": system_health,
            "models": {
                "status": model_status,
                "metrics": model_metrics
            },
            "api": {
                "key_configured": api_key_status
            },
            "timestamp": system_health.get("uptime", 0)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get detailed system metrics."""
    try:
        # Update system metrics
        system_monitor.update_system_metrics()
        
        return {
            "system": system_monitor.get_system_health(),
            "models": model_monitor.get_model_metrics()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        } 