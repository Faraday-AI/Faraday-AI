"""
Progress Service

This module provides progress tracking functionality for the physical education system.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db

logger = logging.getLogger(__name__)

class ProgressEntry(BaseModel):
    """Model for progress entries."""
    progress_id: str
    student_id: str
    activity_id: str
    metric_type: str
    value: float
    unit: str
    recorded_at: datetime
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ProgressService:
    """Service for managing progress tracking in the physical education system."""
    
    def __init__(self, db: Session = None):
        self.logger = logging.getLogger("progress_service")
        self.db = db
        self._progress_entries = {}
        self._progress_counter = 0
        
    async def record_progress(
        self,
        student_id: str,
        activity_id: str,
        metric_type: str,
        value: float,
        unit: str,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record a progress entry."""
        try:
            self._progress_counter += 1
            progress_id = f"progress_{self._progress_counter:06d}"
            
            progress_entry = ProgressEntry(
                progress_id=progress_id,
                student_id=student_id,
                activity_id=activity_id,
                metric_type=metric_type,
                value=value,
                unit=unit,
                recorded_at=datetime.utcnow(),
                notes=notes,
                metadata=metadata or {}
            )
            
            self._progress_entries[progress_id] = progress_entry
            
            self.logger.info(f"Progress recorded for student {student_id}: {metric_type} = {value} {unit}")
            
            return {
                "progress_id": progress_id,
                "status": "recorded",
                "message": "Progress recorded successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error recording progress: {str(e)}")
            raise
    
    async def get_student_progress(
        self,
        student_id: str,
        activity_id: Optional[str] = None,
        metric_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get progress entries for a student."""
        try:
            student_progress = [
                p for p in self._progress_entries.values()
                if p.student_id == student_id
            ]
            
            # Apply filters
            if activity_id:
                student_progress = [p for p in student_progress if p.activity_id == activity_id]
            
            if metric_type:
                student_progress = [p for p in student_progress if p.metric_type == metric_type]
            
            if start_date:
                student_progress = [p for p in student_progress if p.recorded_at >= start_date]
            
            if end_date:
                student_progress = [p for p in student_progress if p.recorded_at <= end_date]
            
            # Sort by recorded_at (newest first)
            student_progress.sort(key=lambda x: x.recorded_at, reverse=True)
            
            # Apply pagination
            student_progress = student_progress[offset:offset + limit]
            
            return [entry.dict() for entry in student_progress]
            
        except Exception as e:
            self.logger.error(f"Error getting student progress: {str(e)}")
            return []
    
    async def get_progress_summary(
        self,
        student_id: str,
        activity_id: Optional[str] = None,
        metric_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get a summary of student progress."""
        try:
            progress_entries = await self.get_student_progress(
                student_id=student_id,
                activity_id=activity_id,
                metric_type=metric_type
            )
            
            if not progress_entries:
                return {
                    "student_id": student_id,
                    "total_entries": 0,
                    "summary": "No progress data available"
                }
            
            # Calculate statistics
            values = [entry["value"] for entry in progress_entries]
            latest_entry = progress_entries[0]  # Already sorted by newest first
            
            summary = {
                "student_id": student_id,
                "total_entries": len(progress_entries),
                "latest_value": latest_entry["value"],
                "latest_unit": latest_entry["unit"],
                "latest_metric": latest_entry["metric_type"],
                "latest_date": latest_entry["recorded_at"],
                "min_value": min(values),
                "max_value": max(values),
                "avg_value": sum(values) / len(values),
                "improvement": latest_entry["value"] - values[-1] if len(values) > 1 else 0,
                "improvement_percentage": (
                    ((latest_entry["value"] - values[-1]) / values[-1] * 100)
                    if len(values) > 1 and values[-1] != 0 else 0
                )
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting progress summary: {str(e)}")
            return {"error": str(e)}
    
    async def get_progress_trends(
        self,
        student_id: str,
        metric_type: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get progress trends for a specific metric."""
        try:
            from datetime import timedelta
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            progress_entries = await self.get_student_progress(
                student_id=student_id,
                metric_type=metric_type,
                start_date=start_date,
                end_date=end_date
            )
            
            if not progress_entries:
                return {
                    "student_id": student_id,
                    "metric_type": metric_type,
                    "trend": "no_data",
                    "data_points": []
                }
            
            # Sort by date for trend analysis
            progress_entries.sort(key=lambda x: x["recorded_at"])
            
            # Calculate trend
            if len(progress_entries) >= 2:
                first_value = progress_entries[0]["value"]
                last_value = progress_entries[-1]["value"]
                
                if last_value > first_value:
                    trend = "improving"
                elif last_value < first_value:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            return {
                "student_id": student_id,
                "metric_type": metric_type,
                "trend": trend,
                "data_points": progress_entries,
                "period_days": days
            }
            
        except Exception as e:
            self.logger.error(f"Error getting progress trends: {str(e)}")
            return {"error": str(e)}
    
    async def compare_students(
        self,
        student_ids: List[str],
        metric_type: str,
        activity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compare progress between multiple students."""
        try:
            comparison_data = {}
            
            for student_id in student_ids:
                progress_entries = await self.get_student_progress(
                    student_id=student_id,
                    activity_id=activity_id,
                    metric_type=metric_type
                )
                
                if progress_entries:
                    latest_entry = progress_entries[0]
                    values = [entry["value"] for entry in progress_entries]
                    
                    comparison_data[student_id] = {
                        "latest_value": latest_entry["value"],
                        "latest_date": latest_entry["recorded_at"],
                        "total_entries": len(progress_entries),
                        "avg_value": sum(values) / len(values),
                        "min_value": min(values),
                        "max_value": max(values)
                    }
                else:
                    comparison_data[student_id] = {
                        "latest_value": None,
                        "latest_date": None,
                        "total_entries": 0,
                        "avg_value": None,
                        "min_value": None,
                        "max_value": None
                    }
            
            return {
                "metric_type": metric_type,
                "activity_id": activity_id,
                "comparison_data": comparison_data
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing students: {str(e)}")
            return {"error": str(e)}
    
    async def get_progress_goals(
        self,
        student_id: str,
        metric_type: str
    ) -> Dict[str, Any]:
        """Get progress goals for a student and metric."""
        try:
            # Mock implementation - in real system, this would fetch from goals table
            progress_entries = await self.get_student_progress(
                student_id=student_id,
                metric_type=metric_type
            )
            
            if not progress_entries:
                return {
                    "student_id": student_id,
                    "metric_type": metric_type,
                    "current_value": None,
                    "goal_value": None,
                    "progress_percentage": 0,
                    "status": "no_data"
                }
            
            current_value = progress_entries[0]["value"]
            
            # Mock goal values based on metric type
            goal_values = {
                "endurance": 30,  # minutes
                "strength": 100,  # lbs
                "flexibility": 90,  # degrees
                "speed": 15,  # seconds for 100m
                "accuracy": 95  # percentage
            }
            
            goal_value = goal_values.get(metric_type, 100)
            progress_percentage = min(100, (current_value / goal_value) * 100)
            
            if progress_percentage >= 100:
                status = "achieved"
            elif progress_percentage >= 75:
                status = "on_track"
            elif progress_percentage >= 50:
                status = "needs_improvement"
            else:
                status = "behind"
            
            return {
                "student_id": student_id,
                "metric_type": metric_type,
                "current_value": current_value,
                "goal_value": goal_value,
                "progress_percentage": round(progress_percentage, 2),
                "status": status
            }
            
        except Exception as e:
            self.logger.error(f"Error getting progress goals: {str(e)}")
            return {"error": str(e)}
    
    async def export_progress_data(
        self,
        student_id: str,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export progress data for a student."""
        try:
            progress_entries = await self.get_student_progress(student_id=student_id)
            
            if format.lower() == "csv":
                # Mock CSV export
                csv_data = "progress_id,student_id,activity_id,metric_type,value,unit,recorded_at\n"
                for entry in progress_entries:
                    csv_data += f"{entry['progress_id']},{entry['student_id']},{entry['activity_id']},{entry['metric_type']},{entry['value']},{entry['unit']},{entry['recorded_at']}\n"
                
                return {
                    "format": "csv",
                    "data": csv_data,
                    "filename": f"progress_{student_id}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
                }
            else:
                # JSON export
                return {
                    "format": "json",
                    "data": progress_entries,
                    "filename": f"progress_{student_id}_{datetime.utcnow().strftime('%Y%m%d')}.json"
                }
            
        except Exception as e:
            self.logger.error(f"Error exporting progress data: {str(e)}")
            return {"error": str(e)} 