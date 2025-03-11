from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from uuid import uuid4

class PassType(Enum):
    RESTROOM = "restroom"
    NURSE = "nurse"
    OFFICE = "office"
    LIBRARY = "library"
    COUNSELOR = "counselor"
    OTHER = "other"

class PassStatus(Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    DENIED = "denied"

@dataclass
class HallPass:
    id: str
    student_id: str
    teacher_id: str
    pass_type: PassType
    destination: str
    start_time: datetime
    expected_duration: timedelta
    actual_duration: Optional[timedelta] = None
    status: PassStatus = PassStatus.REQUESTED
    route: List[str] = None
    violations: List[str] = None

class HallPassSystem:
    """
    AI-powered system for managing digital hall passes and student movement tracking
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_passes: Dict[str, HallPass] = {}
        self.student_history: Dict[str, List[HallPass]] = {}
        self.location_limits: Dict[str, int] = {}
        self.time_limits: Dict[PassType, timedelta] = {
            PassType.RESTROOM: timedelta(minutes=5),
            PassType.NURSE: timedelta(minutes=15),
            PassType.OFFICE: timedelta(minutes=10),
            PassType.LIBRARY: timedelta(minutes=10),
            PassType.COUNSELOR: timedelta(minutes=30),
            PassType.OTHER: timedelta(minutes=10)
        }
        
    async def request_hall_pass(self, student_id: str, teacher_id: str, 
                              pass_type: PassType, destination: str) -> Dict:
        """Request a new hall pass with AI validation"""
        try:
            # Check student eligibility
            if not await self._check_student_eligibility(student_id):
                return {
                    "status": "denied",
                    "reason": "Student has exceeded pass limits or has active violations"
                }
            
            # Check location capacity
            if not await self._check_location_capacity(destination):
                return {
                    "status": "denied",
                    "reason": "Destination is at capacity"
                }
            
            # Create new pass
            pass_id = str(uuid4())
            hall_pass = HallPass(
                id=pass_id,
                student_id=student_id,
                teacher_id=teacher_id,
                pass_type=pass_type,
                destination=destination,
                start_time=datetime.utcnow(),
                expected_duration=self.time_limits[pass_type],
                route=[],
                violations=[]
            )
            
            self.active_passes[pass_id] = hall_pass
            
            # Start monitoring
            await self._start_pass_monitoring(pass_id)
            
            return {
                "status": "approved",
                "pass_id": pass_id,
                "expected_duration": self.time_limits[pass_type].total_seconds()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create hall pass: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def update_pass_location(self, pass_id: str, location: str) -> Dict:
        """Update student location and check for violations"""
        try:
            if pass_id not in self.active_passes:
                return {"status": "error", "message": "Pass not found"}
                
            hall_pass = self.active_passes[pass_id]
            hall_pass.route.append(location)
            
            # Check for route violations
            violations = await self._check_route_violations(hall_pass)
            if violations:
                hall_pass.violations.extend(violations)
                await self._send_violation_alerts(hall_pass)
            
            return {
                "status": "updated",
                "location": location,
                "violations": violations
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update pass location: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def complete_hall_pass(self, pass_id: str) -> Dict:
        """Complete an active hall pass"""
        try:
            if pass_id not in self.active_passes:
                return {"status": "error", "message": "Pass not found"}
                
            hall_pass = self.active_passes[pass_id]
            hall_pass.status = PassStatus.COMPLETED
            hall_pass.actual_duration = datetime.utcnow() - hall_pass.start_time
            
            # Update student history
            student_id = hall_pass.student_id
            if student_id not in self.student_history:
                self.student_history[student_id] = []
            self.student_history[student_id].append(hall_pass)
            
            # Remove from active passes
            del self.active_passes[pass_id]
            
            return {
                "status": "completed",
                "duration": hall_pass.actual_duration.total_seconds(),
                "violations": hall_pass.violations
            }
            
        except Exception as e:
            self.logger.error(f"Failed to complete hall pass: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def generate_student_report(self, student_id: str) -> Dict:
        """Generate a report of student's hall pass usage"""
        try:
            history = self.student_history.get(student_id, [])
            
            total_passes = len(history)
            total_violations = sum(len(p.violations) for p in history)
            avg_duration = sum((p.actual_duration.total_seconds() for p in history), 0) / total_passes if total_passes > 0 else 0
            
            return {
                "student_id": student_id,
                "total_passes": total_passes,
                "total_violations": total_violations,
                "average_duration": avg_duration,
                "pass_history": [self._format_pass_record(p) for p in history]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate student report: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _check_student_eligibility(self, student_id: str) -> bool:
        """Check if student is eligible for a new hall pass"""
        # Check active passes
        if any(p.student_id == student_id for p in self.active_passes.values()):
            return False
            
        # Check recent history
        history = self.student_history.get(student_id, [])
        recent_passes = [p for p in history if 
                        (datetime.utcnow() - p.start_time).total_seconds() < 3600]  # Last hour
        
        if len(recent_passes) >= 3:  # Max 3 passes per hour
            return False
            
        return True
    
    async def _check_location_capacity(self, location: str) -> bool:
        """Check if destination has capacity for more students"""
        current_count = sum(1 for p in self.active_passes.values() 
                          if p.destination == location)
        return current_count < self.location_limits.get(location, 5)
    
    async def _start_pass_monitoring(self, pass_id: str):
        """Start monitoring an active hall pass"""
        asyncio.create_task(self._monitor_pass(pass_id))
    
    async def _monitor_pass(self, pass_id: str):
        """Monitor pass duration and movement"""
        while pass_id in self.active_passes:
            try:
                hall_pass = self.active_passes[pass_id]
                duration = datetime.utcnow() - hall_pass.start_time
                
                # Check for timeout
                if duration > hall_pass.expected_duration:
                    hall_pass.violations.append("Time limit exceeded")
                    await self._send_violation_alerts(hall_pass)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error monitoring pass {pass_id}: {str(e)}")
                await asyncio.sleep(5)
    
    async def _check_route_violations(self, hall_pass: HallPass) -> List[str]:
        """Check for unauthorized movement or route violations"""
        violations = []
        if len(hall_pass.route) < 2:
            return violations
            
        current = hall_pass.route[-1]
        previous = hall_pass.route[-2]
        
        # Check for unauthorized locations
        if current not in self._get_allowed_locations(hall_pass.pass_type):
            violations.append(f"Unauthorized location: {current}")
            
        # Check for excessive movement
        if len(hall_pass.route) > hall_pass.expected_duration.total_seconds() / 30:
            violations.append("Excessive movement detected")
            
        return violations
    
    async def _send_violation_alerts(self, hall_pass: HallPass):
        """Send alerts for pass violations"""
        # TODO: Implement notification system integration
        self.logger.warning(f"Violations detected for pass {hall_pass.id}: {hall_pass.violations}")
    
    def _get_allowed_locations(self, pass_type: PassType) -> List[str]:
        """Get allowed locations for pass type"""
        # Define allowed routes for each pass type
        routes = {
            PassType.RESTROOM: ["hallway", "restroom"],
            PassType.NURSE: ["hallway", "nurse_office"],
            PassType.OFFICE: ["hallway", "main_office"],
            PassType.LIBRARY: ["hallway", "library"],
            PassType.COUNSELOR: ["hallway", "counseling_office"],
            PassType.OTHER: ["hallway"]
        }
        return routes.get(pass_type, [])
    
    def _format_pass_record(self, hall_pass: HallPass) -> Dict:
        """Format hall pass record for reporting"""
        return {
            "pass_id": hall_pass.id,
            "type": hall_pass.pass_type.value,
            "start_time": hall_pass.start_time.isoformat(),
            "duration": hall_pass.actual_duration.total_seconds() if hall_pass.actual_duration else None,
            "status": hall_pass.status.value,
            "violations": hall_pass.violations
        } 