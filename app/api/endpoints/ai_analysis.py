from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, WebSocket, Header
from typing import List, Dict, Any, Optional
from app.services.ai_analytics import get_ai_analytics_service, AIAnalytics
from app.services.ai_vision import get_ai_vision_service, AIVisionAnalysis
from app.services.ai_voice import get_ai_voice_service, AIVoiceAnalysis
from app.services.ai_emotion import get_ai_emotion_service, AIEmotionAnalysis
from app.services.ai_group import get_ai_group_service, AIGroupAnalysis
import json
import numpy as np

router = APIRouter()

@router.post("/analytics/performance")
async def analyze_student_performance(
    student_data: Dict[str, Any],
    lesson_history: List[Dict[str, Any]],
    ai_service: AIAnalytics = Depends(get_ai_analytics_service)
) -> Dict[str, Any]:
    """
    Analyze student performance and provide AI-powered recommendations.
    
    This endpoint:
    1. Predicts future performance
    2. Identifies learning patterns
    3. Suggests personalized interventions
    4. Tracks progress metrics
    5. Generates actionable insights
    """
    try:
        return await ai_service.predict_student_performance(student_data, lesson_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/behavior")
async def analyze_behavior_patterns(
    student_data: Dict[str, Any],
    classroom_data: Dict[str, Any],
    ai_service: AIAnalytics = Depends(get_ai_analytics_service)
) -> Dict[str, Any]:
    """
    Analyze student behavior patterns and engagement levels.
    
    This endpoint:
    1. Identifies behavior patterns
    2. Measures engagement
    3. Suggests interventions
    4. Provides support strategies
    5. Tracks social-emotional metrics
    """
    try:
        return await ai_service.analyze_behavior_patterns(student_data, classroom_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/progress-report")
async def generate_progress_report(
    student_data: Dict[str, Any],
    time_period: str,
    ai_service: AIAnalytics = Depends(get_ai_analytics_service)
) -> Dict[str, Any]:
    """
    Generate comprehensive AI-enhanced progress reports.
    
    This endpoint:
    1. Analyzes performance trends
    2. Identifies achievements
    3. Highlights growth areas
    4. Suggests next steps
    5. Provides visualizations
    """
    try:
        return await ai_service.generate_progress_report(student_data, time_period)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vision/movement-analysis")
async def analyze_movement(
    video: UploadFile = File(...),
    movement_type: str = None,
    ai_service: AIVisionAnalysis = Depends(get_ai_vision_service)
) -> Dict[str, Any]:
    """
    Analyze physical movements using AI vision technology.
    
    This endpoint:
    1. Processes movement video
    2. Analyzes form and technique
    3. Provides feedback
    4. Generates visualizations
    5. Suggests improvements
    """
    try:
        # Save uploaded video temporarily
        video_path = f"temp/{video.filename}"
        with open(video_path, "wb") as buffer:
            buffer.write(await video.read())
        
        return await ai_service.analyze_movement(video_path, movement_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vision/form-feedback")
async def generate_form_feedback(
    video: UploadFile = File(...),
    exercise_type: str = None,
    ai_service: AIVisionAnalysis = Depends(get_ai_vision_service)
) -> Dict[str, Any]:
    """
    Generate real-time form feedback for physical exercises.
    
    This endpoint:
    1. Analyzes exercise form
    2. Provides real-time feedback
    3. Identifies form issues
    4. Suggests corrections
    5. Ensures safety
    """
    try:
        # Save uploaded video temporarily
        video_path = f"temp/{video.filename}"
        with open(video_path, "wb") as buffer:
            buffer.write(await video.read())
        
        return await ai_service.generate_form_feedback(video_path, exercise_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/batch-analysis")
async def perform_batch_analysis(
    student_data: List[Dict[str, Any]],
    analysis_type: str,
    ai_service: AIAnalytics = Depends(get_ai_analytics_service)
) -> Dict[str, Any]:
    """
    Perform batch analysis on multiple students.
    
    This endpoint:
    1. Processes multiple student records
    2. Generates comparative analysis
    3. Identifies patterns
    4. Provides group insights
    5. Suggests interventions
    """
    try:
        results = []
        for student in student_data:
            if analysis_type == "performance":
                result = await ai_service.predict_student_performance(
                    student,
                    student.get("lesson_history", [])
                )
            elif analysis_type == "behavior":
                result = await ai_service.analyze_behavior_patterns(
                    student,
                    student.get("classroom_data", {})
                )
            else:
                result = await ai_service.generate_progress_report(
                    student,
                    student.get("time_period", "weekly")
                )
            results.append(result)
            
        return {
            "individual_results": results,
            "group_analysis": self._analyze_group_results(results),
            "recommendations": self._generate_group_recommendations(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _analyze_group_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze results across multiple students."""
    return {
        "performance_distribution": _calculate_distribution([r["prediction_score"] for r in results]),
        "common_patterns": _identify_common_patterns(results),
        "group_trends": _analyze_trends(results)
    }

def _generate_group_recommendations(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate recommendations based on group analysis."""
    recommendations = []
    patterns = _identify_common_patterns(results)
    
    for pattern in patterns:
        recommendations.append({
            "pattern": pattern,
            "intervention": _suggest_intervention(pattern),
            "priority": _calculate_pattern_priority(pattern, results)
        })
    
    return recommendations

def _calculate_distribution(scores: List[float]) -> Dict[str, float]:
    """Calculate statistical distribution of scores."""
    return {
        "mean": float(np.mean(scores)),
        "median": float(np.median(scores)),
        "std": float(np.std(scores)),
        "min": float(min(scores)),
        "max": float(max(scores))
    }

def _identify_common_patterns(results: List[Dict[str, Any]]) -> List[str]:
    """Identify common patterns across multiple results."""
    patterns = []
    recommendations = [r.get("recommendations", []) for r in results]
    
    # Flatten recommendations
    flat_recommendations = [
        item for sublist in recommendations
        for item in sublist
    ]
    
    # Count recommendation frequencies
    from collections import Counter
    recommendation_counts = Counter(
        [r["content"] for r in flat_recommendations]
    )
    
    # Return most common patterns
    return [
        pattern for pattern, count in recommendation_counts.most_common(5)
    ]

def _analyze_trends(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze trends across multiple results."""
    return {
        "performance_trend": _calculate_trend([r["prediction_score"] for r in results]),
        "engagement_trend": _calculate_trend([r.get("engagement_metrics", {}).get("overall", 0) for r in results]),
        "progress_trend": _calculate_trend([r.get("progress_metrics", {}).get("overall", 0) for r in results])
    }

def _calculate_trend(values: List[float]) -> Dict[str, float]:
    """Calculate trend metrics for a series of values."""
    return {
        "slope": float(np.polyfit(range(len(values)), values, 1)[0]),
        "correlation": float(np.corrcoef(range(len(values)), values)[0, 1]),
        "variance": float(np.var(values))
    }

def _suggest_intervention(pattern: str) -> Dict[str, Any]:
    """Suggest intervention based on identified pattern."""
    return {
        "type": "group_intervention",
        "description": f"Address common pattern: {pattern}",
        "steps": [
            "Identify affected students",
            "Develop targeted intervention",
            "Implement support strategies",
            "Monitor progress",
            "Adjust approach as needed"
        ]
    }

def _calculate_pattern_priority(pattern: str, results: List[Dict[str, Any]]) -> str:
    """Calculate priority level for identified pattern."""
    impact_count = sum(
        1 for r in results
        if any(pattern in rec["content"] for rec in r.get("recommendations", []))
    )
    
    impact_percentage = impact_count / len(results)
    
    if impact_percentage > 0.7:
        return "high"
    elif impact_percentage > 0.3:
        return "medium"
    return "low"

@router.post("/voice/coaching-analysis")
async def analyze_coaching_voice(
    audio: UploadFile = File(...),
    context: Dict[str, Any] = None,
    ai_service: AIVoiceAnalysis = Depends(get_ai_voice_service)
) -> Dict[str, Any]:
    """
    Analyze coaching voice characteristics and provide feedback.
    
    This endpoint:
    1. Analyzes voice clarity and articulation
    2. Evaluates tone and enthusiasm
    3. Assesses pacing and timing
    4. Provides improvement suggestions
    5. Generates engagement metrics
    """
    try:
        # Save uploaded audio temporarily
        audio_path = f"temp/{audio.filename}"
        with open(audio_path, "wb") as buffer:
            buffer.write(await audio.read())
        
        return await ai_service.analyze_coaching_voice(audio_path, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emotion/student-analysis")
async def analyze_student_emotions(
    video: UploadFile = File(...),
    context: Dict[str, Any] = None,
    ai_service: AIEmotionAnalysis = Depends(get_ai_emotion_service)
) -> Dict[str, Any]:
    """
    Analyze student emotions during physical activities.
    
    This endpoint:
    1. Detects emotional states
    2. Analyzes engagement patterns
    3. Assesses motivation levels
    4. Identifies key moments
    5. Provides activity recommendations
    """
    try:
        # Save uploaded video temporarily
        video_path = f"temp/{video.filename}"
        with open(video_path, "wb") as buffer:
            buffer.write(await video.read())
        
        return await ai_service.analyze_student_emotions(video_path, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/group/dynamics-analysis")
async def analyze_group_dynamics(
    group_data: Dict[str, Any],
    activity_context: Dict[str, Any] = None,
    ai_service: AIGroupAnalysis = Depends(get_ai_group_service)
) -> Dict[str, Any]:
    """
    Analyze group dynamics and team interactions.
    
    This endpoint:
    1. Analyzes team cohesion
    2. Identifies leadership patterns
    3. Evaluates communication effectiveness
    4. Assesses collaboration quality
    5. Provides intervention strategies
    
    The group_data should include:
    - List of students with IDs
    - Interaction records between students
    - Activity type and duration
    - Group formation method
    - Previous group history (if any)
    """
    try:
        return await ai_service.analyze_group_dynamics(group_data, activity_context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/group/start-monitoring")
async def start_group_monitoring(
    session_id: str,
    group_data: Dict[str, Any],
    monitoring_interval: int = 30,
    ai_service: AIGroupAnalysis = Depends(get_ai_group_service)
) -> Dict[str, Any]:
    """
    Start real-time monitoring of group dynamics.
    
    This endpoint:
    1. Initializes monitoring session
    2. Sets up real-time tracking
    3. Configures alert thresholds
    4. Begins data collection
    5. Activates analysis pipeline
    
    The group_data should include:
    - List of students with IDs
    - Initial group configuration
    - Activity parameters
    - Monitoring preferences
    - Alert settings
    """
    try:
        return await ai_service.start_real_time_monitoring(
            session_id,
            group_data,
            monitoring_interval
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/group/update-session/{session_id}")
async def update_group_session(
    session_id: str,
    interactions: List[Dict[str, Any]],
    ai_service: AIGroupAnalysis = Depends(get_ai_group_service)
) -> Dict[str, Any]:
    """
    Update monitoring session with new interaction data.
    
    This endpoint:
    1. Processes new interactions
    2. Updates group metrics
    3. Checks for alerts
    4. Updates visualizations
    5. Returns current status
    """
    try:
        return await ai_service.update_session_data(session_id, interactions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/group/session-status/{session_id}")
async def get_group_session_status(
    session_id: str,
    ai_service: AIGroupAnalysis = Depends(get_ai_group_service)
) -> Dict[str, Any]:
    """
    Get current status of monitoring session.
    
    This endpoint returns:
    1. Session duration
    2. Current metrics
    3. Recent alerts
    4. Interaction counts
    5. Real-time insights
    """
    try:
        return await ai_service.get_session_status(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/group/end-session/{session_id}")
async def end_group_session(
    session_id: str,
    ai_service: AIGroupAnalysis = Depends(get_ai_group_service)
) -> Dict[str, Any]:
    """
    End monitoring session and generate final analysis.
    
    This endpoint:
    1. Processes remaining data
    2. Generates session summary
    3. Provides trend analysis
    4. Creates visualizations
    5. Offers recommendations
    """
    try:
        return await ai_service.end_session(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/group/ws/{session_id}")
async def group_monitoring_websocket(
    websocket: WebSocket,
    session_id: str,
    token: Optional[str] = Header(None),
    ai_service: AIGroupAnalysis = Depends(get_ai_group_service)
):
    """
    WebSocket endpoint for real-time group monitoring.
    
    This endpoint:
    1. Authenticates the connection
    2. Verifies session access
    3. Establishes secure WebSocket
    4. Manages role-based updates
    5. Handles secure disconnection
    
    Authentication:
    - Requires JWT token in header
    - Validates user permissions
    - Enforces role-based access
    
    Message types:
    - session_state: Initial session state
    - interactions_processed: New interactions processed
    - new_alerts: New alerts generated
    - metrics_updated: Updated group metrics
    - session_ended: Final session summary
    
    Role-based permissions:
    - Teachers: Full access (read/write)
    - Observers: Read-only access
    """
    if not token:
        await websocket.close(code=4001)
        return
        
    await ai_service.connect_websocket(session_id, websocket, token) 