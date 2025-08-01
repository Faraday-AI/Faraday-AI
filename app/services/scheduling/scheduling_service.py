"""
Scheduling Service

This module provides scheduling functionality for the physical education system.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db

logger = logging.getLogger(__name__)

class Schedule(BaseModel):
    """Model for schedules."""
    schedule_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    activity_type: str
    location: str
    max_participants: Optional[int] = None
    current_participants: int = 0
    instructor_id: Optional[str] = None
    status: str = "scheduled"
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class SchedulingService:
    """Service for managing schedules in the physical education system."""
    
    def __init__(self, db: Session = None):
        self.logger = logging.getLogger("scheduling_service")
        self.db = db
        self._schedules = {}
        self._schedule_counter = 0
        
    async def create_schedule(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        activity_type: str,
        location: str,
        instructor_id: Optional[str] = None,
        max_participants: Optional[int] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new schedule."""
        try:
            # Validate time range
            if start_time >= end_time:
                raise ValueError("Start time must be before end time")
            
            # Check for conflicts
            conflicts = await self._check_schedule_conflicts(
                location, start_time, end_time
            )
            if conflicts:
                return {
                    "success": False,
                    "error": "Schedule conflicts detected",
                    "conflicts": conflicts
                }
            
            self._schedule_counter += 1
            schedule_id = f"schedule_{self._schedule_counter:06d}"
            
            schedule = Schedule(
                schedule_id=schedule_id,
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                activity_type=activity_type,
                location=location,
                max_participants=max_participants,
                instructor_id=instructor_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            self._schedules[schedule_id] = schedule
            
            self.logger.info(f"Schedule created: {title} at {location}")
            
            return {
                "success": True,
                "schedule_id": schedule_id,
                "message": "Schedule created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error creating schedule: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_schedule(
        self,
        schedule_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get schedule details by ID."""
        try:
            schedule = self._schedules.get(schedule_id)
            if schedule:
                return schedule.dict()
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting schedule: {str(e)}")
            return None
    
    async def list_schedules(
        self,
        location: Optional[str] = None,
        activity_type: Optional[str] = None,
        instructor_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List schedules with optional filtering."""
        try:
            schedules = list(self._schedules.values())
            
            # Apply filters
            if location:
                schedules = [s for s in schedules if s.location == location]
            
            if activity_type:
                schedules = [s for s in schedules if s.activity_type == activity_type]
            
            if instructor_id:
                schedules = [s for s in schedules if s.instructor_id == instructor_id]
            
            if start_date:
                schedules = [s for s in schedules if s.start_time >= start_date]
            
            if end_date:
                schedules = [s for s in schedules if s.end_time <= end_date]
            
            if status:
                schedules = [s for s in schedules if s.status == status]
            
            # Sort by start_time
            schedules.sort(key=lambda x: x.start_time)
            
            # Apply pagination
            schedules = schedules[offset:offset + limit]
            
            return [schedule.dict() for schedule in schedules]
            
        except Exception as e:
            self.logger.error(f"Error listing schedules: {str(e)}")
            return []
    
    async def update_schedule(
        self,
        schedule_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update schedule details."""
        try:
            if schedule_id not in self._schedules:
                return False
            
            schedule = self._schedules[schedule_id]
            
            # Update allowed fields
            allowed_fields = [
                "title", "description", "start_time", "end_time",
                "activity_type", "location", "max_participants",
                "instructor_id", "status", "metadata"
            ]
            
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(schedule, field, value)
            
            schedule.updated_at = datetime.utcnow()
            
            self.logger.info(f"Schedule {schedule_id} updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating schedule: {str(e)}")
            return False
    
    async def delete_schedule(
        self,
        schedule_id: str
    ) -> bool:
        """Delete a schedule."""
        try:
            if schedule_id not in self._schedules:
                return False
            
            del self._schedules[schedule_id]
            self.logger.info(f"Schedule {schedule_id} deleted")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting schedule: {str(e)}")
            return False
    
    async def add_participant(
        self,
        schedule_id: str,
        participant_id: str
    ) -> Dict[str, Any]:
        """Add a participant to a schedule."""
        try:
            if schedule_id not in self._schedules:
                return {"success": False, "error": "Schedule not found"}
            
            schedule = self._schedules[schedule_id]
            
            # Check if schedule is full
            if schedule.max_participants and schedule.current_participants >= schedule.max_participants:
                return {"success": False, "error": "Schedule is full"}
            
            # Check if schedule is in the past
            if schedule.start_time < datetime.utcnow():
                return {"success": False, "error": "Cannot join past schedule"}
            
            # Mock participant tracking
            if "participants" not in schedule.metadata:
                schedule.metadata["participants"] = []
            
            if participant_id not in schedule.metadata["participants"]:
                schedule.metadata["participants"].append(participant_id)
                schedule.current_participants += 1
                schedule.updated_at = datetime.utcnow()
                
                self.logger.info(f"Participant {participant_id} added to schedule {schedule_id}")
                return {"success": True, "message": "Participant added successfully"}
            else:
                return {"success": False, "error": "Participant already registered"}
            
        except Exception as e:
            self.logger.error(f"Error adding participant: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def remove_participant(
        self,
        schedule_id: str,
        participant_id: str
    ) -> Dict[str, Any]:
        """Remove a participant from a schedule."""
        try:
            if schedule_id not in self._schedules:
                return {"success": False, "error": "Schedule not found"}
            
            schedule = self._schedules[schedule_id]
            
            if "participants" in schedule.metadata and participant_id in schedule.metadata["participants"]:
                schedule.metadata["participants"].remove(participant_id)
                schedule.current_participants = max(0, schedule.current_participants - 1)
                schedule.updated_at = datetime.utcnow()
                
                self.logger.info(f"Participant {participant_id} removed from schedule {schedule_id}")
                return {"success": True, "message": "Participant removed successfully"}
            else:
                return {"success": False, "error": "Participant not found in schedule"}
            
        except Exception as e:
            self.logger.error(f"Error removing participant: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_schedule_conflicts(
        self,
        location: str,
        start_time: datetime,
        end_time: datetime,
        exclude_schedule_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get schedule conflicts for a time range and location."""
        try:
            conflicts = []
            
            for schedule in self._schedules.values():
                if schedule.schedule_id == exclude_schedule_id:
                    continue
                
                if schedule.location != location:
                    continue
                
                # Check for time overlap
                if (schedule.start_time < end_time and schedule.end_time > start_time):
                    conflicts.append({
                        "schedule_id": schedule.schedule_id,
                        "title": schedule.title,
                        "start_time": schedule.start_time.isoformat(),
                        "end_time": schedule.end_time.isoformat(),
                        "activity_type": schedule.activity_type
                    })
            
            return conflicts
            
        except Exception as e:
            self.logger.error(f"Error getting schedule conflicts: {str(e)}")
            return []
    
    async def get_schedule_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get schedule statistics."""
        try:
            schedules = list(self._schedules.values())
            
            # Filter by date range if provided
            if start_date:
                schedules = [s for s in schedules if s.start_time >= start_date]
            if end_date:
                schedules = [s for s in schedules if s.end_time <= end_date]
            
            total_schedules = len(schedules)
            completed_schedules = len([s for s in schedules if s.end_time < datetime.utcnow()])
            upcoming_schedules = len([s for s in schedules if s.start_time > datetime.utcnow()])
            
            # Activity type breakdown
            activity_counts = {}
            for schedule in schedules:
                activity_counts[schedule.activity_type] = activity_counts.get(schedule.activity_type, 0) + 1
            
            # Location breakdown
            location_counts = {}
            for schedule in schedules:
                location_counts[schedule.location] = location_counts.get(schedule.location, 0) + 1
            
            return {
                "total_schedules": total_schedules,
                "completed_schedules": completed_schedules,
                "upcoming_schedules": upcoming_schedules,
                "activity_breakdown": activity_counts,
                "location_breakdown": location_counts
            }
            
        except Exception as e:
            self.logger.error(f"Error getting schedule stats: {str(e)}")
            return {}
    
    # Helper methods
    async def _check_schedule_conflicts(
        self,
        location: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Check for schedule conflicts."""
        return await self.get_schedule_conflicts(location, start_time, end_time) 