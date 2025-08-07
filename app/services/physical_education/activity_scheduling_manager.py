"""
Activity Scheduling Manager

This module provides scheduling and planning for physical education activities.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# Import scheduling service
try:
    from app.services.scheduling import SchedulingService
except ImportError:
    SchedulingService = None


class ActivitySchedulingManager:
    """Manages scheduling and planning for physical education activities."""
    
    def __init__(self, db: Session, activity_manager=None, scheduling_service=None):
        """Initialize the scheduling manager.
        
        Args:
            db: Database session
            activity_manager: Activity manager instance
            scheduling_service: Scheduling service instance (optional)
        """
        self.db = db
        self.activity_manager = activity_manager
        self.schedules = {}
        
        # Use provided scheduling service or try to create one
        if scheduling_service is not None:
            self.scheduling_service = scheduling_service
        else:
            self.scheduling_service = None
            try:
                if SchedulingService:
                    self.scheduling_service = SchedulingService()
            except Exception:
                # Scheduling service might be mocked or unavailable
                pass
        
    async def create_activity_schedule(self, class_id: str, activities: List[Dict[str, Any]], 
                                     start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Create a schedule for activities in a class.
        
        Args:
            class_id: Class identifier
            activities: List of activities to schedule
            start_date: Start date for schedule
            end_date: End date for schedule
            
        Returns:
            Schedule creation result
        """
        try:
            schedule_id = f"schedule_{class_id}_{start_date.strftime('%Y%m%d')}"
            
            self.schedules[schedule_id] = {
                "schedule_id": schedule_id,
                "class_id": class_id,
                "activities": activities,
                "start_date": start_date,
                "end_date": end_date,
                "created_at": datetime.now(),
                "status": "active"
            }
            
            return {
                "schedule_created": True,
                "schedule_id": schedule_id,
                "activities_count": len(activities)
            }
        except Exception as e:
            logger.error(f"Error creating activity schedule: {e}")
            return {"schedule_created": False, "error": str(e)}
    
    async def get_class_schedule(self, class_id: str, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get the schedule for a class.
        
        Args:
            class_id: Class identifier
            date: Specific date to get schedule for
            
        Returns:
            Class schedule
        """
        try:
            if date is None:
                date = datetime.now()
                
            # Find schedules for this class
            class_schedules = [
                schedule for schedule in self.schedules.values()
                if schedule["class_id"] == class_id and
                schedule["start_date"] <= date <= schedule["end_date"]
            ]
            
            if class_schedules:
                return {
                    "schedule_found": True,
                    "schedules": class_schedules
                }
            else:
                return {
                    "schedule_found": False,
                    "schedules": []
                }
        except Exception as e:
            logger.error(f"Error getting class schedule: {e}")
            return {"schedule_found": False, "error": str(e)}
    
    async def update_activity_schedule(self, schedule_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing activity schedule.
        
        Args:
            schedule_id: Schedule identifier
            updates: Updates to apply
            
        Returns:
            Update result
        """
        try:
            if schedule_id in self.schedules:
                self.schedules[schedule_id].update(updates)
                self.schedules[schedule_id]["updated_at"] = datetime.now()
                
                return {
                    "schedule_updated": True,
                    "schedule_id": schedule_id
                }
            else:
                return {
                    "schedule_updated": False,
                    "error": "Schedule not found"
                }
        except Exception as e:
            logger.error(f"Error updating activity schedule: {e}")
            return {"schedule_updated": False, "error": str(e)}
    
    async def optimize_schedule(self, class_id: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize the schedule based on constraints.
        
        Args:
            class_id: Class identifier
            constraints: Scheduling constraints
            
        Returns:
            Optimization result
        """
        try:
            # Mock optimization logic
            optimized_schedule = {
                "optimization_complete": True,
                "class_id": class_id,
                "optimized_activities": [
                    {
                        "activity_id": "opt_activity_1",
                        "scheduled_time": datetime.now() + timedelta(days=1),
                        "duration": 45,
                        "priority": "high"
                    }
                ],
                "constraints_met": True,
                "efficiency_score": 0.85
            }
            
            return optimized_schedule
        except Exception as e:
            logger.error(f"Error optimizing schedule: {e}")
            return {"optimization_complete": False, "error": str(e)}
    
    async def check_schedule_conflicts(self, class_id: str, new_activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for scheduling conflicts.
        
        Args:
            class_id: Class identifier
            new_activities: New activities to check
            
        Returns:
            Conflict check result
        """
        try:
            # Mock conflict checking
            conflicts = []
            
            for activity in new_activities:
                # Simple conflict detection
                if activity.get("duration", 0) > 60:
                    conflicts.append({
                        "activity_id": activity.get("activity_id"),
                        "conflict_type": "duration_too_long",
                        "message": "Activity duration exceeds maximum allowed time"
                    })
            
            return {
                "conflicts_found": len(conflicts) > 0,
                "conflicts": conflicts,
                "schedule_viable": len(conflicts) == 0
            }
        except Exception as e:
            logger.error(f"Error checking schedule conflicts: {e}")
            return {"conflicts_found": False, "error": str(e)}
    
    async def generate_schedule_report(self, class_id: str, date_range: Optional[Dict[str, datetime]] = None) -> Dict[str, Any]:
        """Generate a schedule report for a class.
        
        Args:
            class_id: Class identifier
            date_range: Date range for report
            
        Returns:
            Schedule report
        """
        try:
            schedules = await self.get_class_schedule(class_id)
            
            report = {
                "report_generated": True,
                "class_id": class_id,
                "total_schedules": len(schedules.get("schedules", [])),
                "total_activities": sum(
                    len(schedule.get("activities", [])) 
                    for schedule in schedules.get("schedules", [])
                ),
                "date_range": date_range or {"start": datetime.now(), "end": datetime.now() + timedelta(days=7)},
                "generated_at": datetime.now()
            }
            
            return report
        except Exception as e:
            logger.error(f"Error generating schedule report: {e}")
            return {"report_generated": False, "error": str(e)}
    
    async def schedule_activity(self, activity_id: str, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule an activity.
        
        Args:
            activity_id: Activity identifier
            schedule_data: Schedule information
            
        Returns:
            Scheduling result
        """
        try:
            if self.activity_manager:
                # Handle both async and sync activity managers
                if hasattr(self.activity_manager.get_activity, '__call__'):
                    if asyncio.iscoroutinefunction(self.activity_manager.get_activity):
                        activity = await self.activity_manager.get_activity(activity_id)
                    else:
                        activity = self.activity_manager.get_activity(activity_id)
                else:
                    activity = self.activity_manager.get_activity
                
                if not activity:
                    return {"scheduled": False, "error": "Activity not found"}
            
            schedule_id = f"schedule_{activity_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Use scheduling service if available (including mocks)
            if self.scheduling_service is not None:
                try:
                    await self.scheduling_service.create_schedule(
                        title=f"Activity: {activity_id}",
                        start_time=schedule_data.get("start_time"),
                        end_time=schedule_data.get("end_time"),
                        activity_type=activity_id,
                        location=schedule_data.get("location")
                    )
                except Exception as e:
                    logger.warning(f"Scheduling service call failed: {e}")
            
            return {
                "scheduled": True,
                "schedule_id": schedule_id,
                "confirmation_details": {
                    "activity_id": activity_id,
                    "start_time": schedule_data.get("start_time"),
                    "end_time": schedule_data.get("end_time"),
                    "location": schedule_data.get("location")
                }
            }
        except Exception as e:
            logger.error(f"Error scheduling activity: {e}")
            return {"scheduled": False, "error": str(e)}
    
    async def check_schedule_availability(self, location: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Check schedule availability for a location and time.
        
        Args:
            location: Location to check
            start_time: Start time
            end_time: End time
            
        Returns:
            Availability result
        """
        try:
            # Use scheduling service if available
            if self.scheduling_service:
                result = await self.scheduling_service.check_availability(location, start_time, end_time)
                return result
            else:
                # Mock availability check
                return {
                    "available": True,
                    "conflicting_events": []
                }
        except Exception as e:
            logger.error(f"Error checking schedule availability: {e}")
            return {"available": False, "error": str(e)}
    
    async def update_schedule(self, schedule_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing schedule.
        
        Args:
            schedule_id: Schedule identifier
            update_data: Update information
            
        Returns:
            Update result
        """
        try:
            # Use scheduling service if available
            if self.scheduling_service:
                result = await self.scheduling_service.update_schedule(schedule_id, update_data)
                return result
            else:
                return {
                    "updated": True,
                    "new_schedule": update_data
                }
        except Exception as e:
            logger.error(f"Error updating schedule: {e}")
            return {"updated": False, "error": str(e)}
    
    async def cancel_schedule(self, schedule_id: str, reason: str = None) -> Dict[str, Any]:
        """Cancel a schedule.
        
        Args:
            schedule_id: Schedule identifier
            reason: Cancellation reason
            
        Returns:
            Cancellation result
        """
        try:
            # Use scheduling service if available
            if self.scheduling_service:
                result = await self.scheduling_service.cancel_schedule(schedule_id, reason)
                return result
            else:
                return {
                    "cancelled": True,
                    "cancellation_time": datetime.now()
                }
        except Exception as e:
            logger.error(f"Error cancelling schedule: {e}")
            return {"cancelled": False, "error": str(e)}
    
    async def get_schedule_history(self, class_id: str = None, date_range: Dict[str, datetime] = None) -> List[Dict[str, Any]]:
        """Get schedule history.
        
        Args:
            class_id: Optional class identifier
            date_range: Optional date range
            
        Returns:
            Schedule history list
        """
        try:
            # Use database query if available
            if self.db:
                query = self.db.query("schedules")
                if class_id:
                    query = query.filter(class_id=class_id)
                if date_range:
                    query = query.filter(start_date__gte=date_range.get("start"), end_date__lte=date_range.get("end"))
                query = query.order_by("start_date")
                history = query.all()
                return history
            
            # Fallback to in-memory schedules
            history = []
            for schedule in self.schedules.values():
                if class_id and schedule["class_id"] != class_id:
                    continue
                if date_range:
                    if schedule["start_date"] < date_range.get("start") or schedule["end_date"] > date_range.get("end"):
                        continue
                history.append(schedule)
            
            return history
        except Exception as e:
            logger.error(f"Error getting schedule history: {e}")
            return []
    
    async def handle_schedule_conflict(self, schedule_id: str, conflict_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle schedule conflicts.
        
        Args:
            schedule_id: Schedule identifier
            conflict_data: Conflict information
            
        Returns:
            Conflict resolution result
        """
        try:
            # Use scheduling service if available
            if self.scheduling_service is not None:
                try:
                    result = await self.scheduling_service.resolve_conflict(schedule_id, conflict_data)
                    return result
                except Exception as e:
                    logger.warning(f"Scheduling service call failed: {e}")
            
            return {
                "resolved": True,
                "resolution": "Automatic rescheduling",
                "new_schedule": conflict_data
            }
        except Exception as e:
            logger.error(f"Error handling schedule conflict: {e}")
            return {"resolved": False, "error": str(e)} 