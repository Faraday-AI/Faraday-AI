"""
Collaboration Dashboard API

This module provides the collaboration-related API endpoints for the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.db.session import get_db
from app.dashboard.dependencies import get_current_user
from app.dashboard.services.collaboration.realtime_collaboration_service import RealtimeCollaborationService
from ....schemas.collaboration import (
    CollaborationSession,
    CollaborationDocument,
    CollaborationMetrics,
    CollaborationAnalytics,
    CollaborationWidget
)

router = APIRouter()

@router.get("/sessions", response_model=List[CollaborationSession])
async def get_collaboration_sessions(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = Query(None, description="Filter by session status"),
    include_metrics: bool = Query(True, description="Include session metrics"),
    include_participants: bool = Query(True, description="Include participant details")
):
    """Get all collaboration sessions for the dashboard."""
    collaboration_service = RealtimeCollaborationService()
    
    try:
        sessions = await collaboration_service.get_user_sessions(
            user_id=current_user["id"],
            status=status
        )
        
        if include_metrics:
            for session in sessions:
                session["metrics"] = await collaboration_service.get_session_metrics(session["id"])
                
        if include_participants:
            for session in sessions:
                session["participants"] = await collaboration_service.get_session_participants(session["id"])
                
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=List[CollaborationDocument])
async def get_collaboration_documents(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    include_history: bool = Query(True, description="Include document history"),
    include_locks: bool = Query(True, description="Include lock information")
):
    """Get all collaboration documents for the dashboard."""
    collaboration_service = RealtimeCollaborationService()
    
    try:
        documents = await collaboration_service.get_user_documents(
            user_id=current_user["id"],
            session_id=session_id,
            document_type=document_type
        )
        
        if include_history:
            for doc in documents:
                doc["history"] = await collaboration_service.get_document_history(doc["id"])
                
        if include_locks:
            for doc in documents:
                doc["lock_status"] = await collaboration_service.get_lock_status(doc["id"])
                
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_model=CollaborationMetrics)
async def get_collaboration_metrics(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for metrics"),
    include_sessions: bool = Query(True, description="Include session metrics"),
    include_documents: bool = Query(True, description="Include document metrics"),
    include_participants: bool = Query(True, description="Include participant metrics")
):
    """Get collaboration metrics for the dashboard."""
    collaboration_service = RealtimeCollaborationService()
    
    try:
        metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "total_documents": 0,
            "active_documents": 0,
            "total_participants": 0,
            "active_participants": 0
        }
        
        if include_sessions:
            metrics.update(await collaboration_service.get_session_metrics_summary(
                user_id=current_user["id"],
                time_range=time_range
            ))
            
        if include_documents:
            metrics.update(await collaboration_service.get_document_metrics_summary(
                user_id=current_user["id"],
                time_range=time_range
            ))
            
        if include_participants:
            metrics.update(await collaboration_service.get_participant_metrics_summary(
                user_id=current_user["id"],
                time_range=time_range
            ))
            
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics", response_model=CollaborationAnalytics)
async def get_collaboration_analytics(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for analytics"),
    include_trends: bool = Query(True, description="Include trend analysis"),
    include_patterns: bool = Query(True, description="Include usage patterns"),
    include_insights: bool = Query(True, description="Include collaboration insights")
):
    """Get collaboration analytics for the dashboard."""
    collaboration_service = RealtimeCollaborationService()
    
    try:
        analytics = {
            "summary": {},
            "trends": {},
            "patterns": {},
            "insights": {}
        }
        
        # Get basic analytics summary
        analytics["summary"] = await collaboration_service.get_analytics_summary(
            user_id=current_user["id"],
            time_range=time_range
        )
        
        if include_trends:
            analytics["trends"] = await collaboration_service.get_trend_analysis(
                user_id=current_user["id"],
                time_range=time_range
            )
            
        if include_patterns:
            analytics["patterns"] = await collaboration_service.get_usage_patterns(
                user_id=current_user["id"],
                time_range=time_range
            )
            
        if include_insights:
            analytics["insights"] = await collaboration_service.get_collaboration_insights(
                user_id=current_user["id"],
                time_range=time_range
            )
            
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/widgets", response_model=List[CollaborationWidget])
async def get_collaboration_widgets(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    widget_type: Optional[str] = Query(None, description="Filter by widget type"),
    include_data: bool = Query(True, description="Include widget data"),
    include_config: bool = Query(True, description="Include widget configuration")
):
    """Get collaboration widgets for the dashboard."""
    collaboration_service = RealtimeCollaborationService()
    
    try:
        widgets = await collaboration_service.get_dashboard_widgets(
            user_id=current_user["id"],
            widget_type=widget_type
        )
        
        if include_data:
            for widget in widgets:
                widget["data"] = await collaboration_service.get_widget_data(widget["id"])
                
        if include_config:
            for widget in widgets:
                widget["config"] = await collaboration_service.get_widget_config(widget["id"])
                
        return widgets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{user_id}")
async def collaboration_websocket(
    websocket: WebSocket,
    user_id: str,
    collaboration_service: RealtimeCollaborationService = Depends(RealtimeCollaborationService)
):
    """WebSocket endpoint for real-time collaboration updates."""
    await websocket.accept()
    await collaboration_service.register_websocket(user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await collaboration_service.handle_websocket_message(user_id, message)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
    except WebSocketDisconnect:
        await collaboration_service.unregister_websocket(user_id)
    except Exception as e:
        await collaboration_service.unregister_websocket(user_id)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/widgets/{widget_type}", response_model=Dict[str, Any])
async def get_collaboration_widget_data(
    widget_type: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for widget data"),
    include_metrics: bool = Query(True, description="Include widget metrics"),
    include_config: bool = Query(True, description="Include widget configuration")
):
    """Get data for a specific collaboration widget type."""
    collaboration_service = RealtimeCollaborationService()
    
    try:
        widget_data = await collaboration_service.get_widget_data(
            user_id=current_user["id"],
            widget_type=widget_type,
            time_range=time_range
        )
        
        if include_metrics:
            widget_data["metrics"] = await collaboration_service.get_widget_metrics(
                user_id=current_user["id"],
                widget_type=widget_type,
                time_range=time_range
            )
            
        if include_config:
            widget_data["config"] = await collaboration_service.get_widget_config(
                user_id=current_user["id"],
                widget_type=widget_type
            )
            
        return widget_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/performance", response_model=Dict[str, Any])
async def get_collaboration_performance(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for performance metrics"),
    include_details: bool = Query(True, description="Include detailed performance metrics")
):
    """Get collaboration performance metrics."""
    collaboration_service = RealtimeCollaborationService()
    
    try:
        performance = await collaboration_service.get_performance_metrics(
            user_id=current_user["id"],
            time_range=time_range,
            include_details=include_details
        )
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/engagement", response_model=Dict[str, Any])
async def get_collaboration_engagement(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for engagement metrics"),
    include_details: bool = Query(True, description="Include detailed engagement metrics")
):
    """Get collaboration engagement metrics."""
    collaboration_service = RealtimeCollaborationService()
    
    try:
        engagement = await collaboration_service.get_engagement_metrics(
            user_id=current_user["id"],
            time_range=time_range,
            include_details=include_details
        )
        return engagement
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/recommendations", response_model=List[Dict[str, Any]])
async def get_collaboration_recommendations(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for recommendations"),
    include_impact: bool = Query(True, description="Include impact analysis")
):
    """Get collaboration recommendations."""
    collaboration_service = RealtimeCollaborationService()
    
    try:
        recommendations = await collaboration_service.get_recommendations(
            user_id=current_user["id"],
            time_range=time_range,
            include_impact=include_impact
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/team-performance", response_model=Dict[str, Any])
async def get_team_performance(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for team performance metrics"),
    include_individual: bool = Query(True, description="Include individual performance metrics")
):
    """Get team performance metrics."""
    collaboration_service = RealtimeCollaborationService()
    
    try:
        performance = await collaboration_service.get_team_performance(
            user_id=current_user["id"],
            time_range=time_range,
            include_individual=include_individual
        )
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/feature-adoption", response_model=Dict[str, Any])
async def get_feature_adoption(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for feature adoption metrics"),
    include_trends: bool = Query(True, description="Include adoption trends")
):
    """Get feature adoption metrics."""
    collaboration_service = RealtimeCollaborationService()
    
    try:
        adoption = await collaboration_service.get_feature_adoption(
            user_id=current_user["id"],
            time_range=time_range,
            include_trends=include_trends
        )
        return adoption
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/resource-usage", response_model=Dict[str, Any])
async def get_resource_usage(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for resource usage metrics"),
    include_details: bool = Query(True, description="Include detailed resource usage")
):
    """Get resource usage metrics."""
    collaboration_service = RealtimeCollaborationService()
    
    try:
        usage = await collaboration_service.get_resource_usage(
            user_id=current_user["id"],
            time_range=time_range,
            include_details=include_details
        )
        return usage
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 