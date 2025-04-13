from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os
from pathlib import Path
import networkx as nx
from openpyxl import Workbook
import csv
from pptx import Presentation
from docx import Document
import markdown
# import latex  # Commented out as it's not essential for testing
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import Depends
from fastapi.websockets import WebSocket
import asyncio
import websockets
import aiofiles
from pylatex import Document, Section, Subsection, Command
import holoviews as hv
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, ColumnDataSource
import streamlit as st

from ..models.activity import (
    Activity,
    Exercise,
    Routine,
    RoutineActivity,
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    ActivityCategory,
    StudentActivityPerformance,
    StudentActivityPreference,
    ActivityProgression,
    ActivityPlan,
    ActivityPlanActivity
)
from ..models.student import Student
from ..models.class_ import Class
from app.core.database import get_db  # Updated import path
from .activity_visualization_manager import ActivityVisualizationManager
from .activity_collaboration_manager import ActivityCollaborationManager
from .activity_export_manager import ActivityExportManager
from .activity_analysis_manager import ActivityAnalysisManager

class ActivityManager:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Activity configuration
        self.activity_types = [t.value for t in ActivityType]
        self.difficulty_levels = [d.value for d in DifficultyLevel]
        self.equipment_requirements = [e.value for e in EquipmentRequirement]
        self.categories = [c.value for c in ActivityCategory]
        
        # Visualization configuration
        plt.style.use('default')  # Use default style instead of seaborn
        sns.set_palette("husl")
        
        # Export configuration
        self.export_formats = ['png', 'svg', 'pdf', 'html', 'json', 'xlsx', 'csv', 'pptx', 'docx', 'md', 'tex']
        self.export_dir = Path("exports/visualizations")
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Interactive features configuration
        self.interactive_features = {
            'filtering': True,
            'sorting': True,
            'custom_styling': True,
            'tooltips': True,
            'zoom': True,
            'pan': True,
            'selection': True,
            'animation': True,
            'drill_down': True,
            'annotations': True,
            'custom_metrics': True,
            'comparison': True,
            'export': True,
            'real_time_updates': True,
            'collaborative_annotations': True,
            'custom_filters': True,
            'data_export': True,
            'interactive_legends': True,
            'cross_highlighting': True,
            'live_chat': True,
            'shared_workspace': True,
            'version_history': True
        }

        # WebSocket connections for real-time updates
        self.active_connections: Dict[str, List[WebSocket]] = {}

        # Enhanced interactive features configuration
        self.interactive_features.update({
            'drill_down': True,
            'custom_annotations': True,
            'real_time_collaboration': True,
            'custom_metrics': True,
            'comparison': True,
            'export': True,
            'real_time_updates': True,
            'collaborative_annotations': True,
            'custom_filters': True,
            'data_export': True,
            'interactive_legends': True,
            'cross_highlighting': True,
            'animation': True,
            'zoom': True,
            'pan': True,
            'selection': True,
            'custom_styling': True,
            'filtering': True,
            'sorting': True,
            'tooltips': True
        })

        # WebSocket connections for real-time collaboration
        self.collaborative_sessions: Dict[str, Dict[str, Any]] = {}

        # Add new export formats
        self.export_formats.extend(['latex', 'md'])
        
        # Add new visualization types
        self.visualization_types = ['chord_diagram', 'stream_graph', 'parallel_coordinates', 'network_graph']
        
        # Initialize real-time update system
        self._init_real_time_system()
        
        # Initialize collaborative features
        self._init_collaborative_features()

        # Initialize specialized managers
        self.visualization_manager = ActivityVisualizationManager()
        self.collaboration_manager = ActivityCollaborationManager()
        self.export_manager = ActivityExportManager()
        self.analysis_manager = ActivityAnalysisManager()
        
        # Initialize core settings
        self.settings = {
            'max_activities_per_student': 100,
            'activity_timeout': 3600,  # 1 hour in seconds
            'default_duration': 30,  # minutes
            'min_duration': 5,  # minutes
            'max_duration': 120  # minutes
        }

    def _init_real_time_system(self):
        """Initialize real-time update system."""
        self.real_time_updates = {}
        self.update_callbacks = {}
    
    def _init_collaborative_features(self):
        """Initialize collaborative features."""
        self.annotations = {}
        self.chat_messages = {}
        self.workspace_versions = {}

    async def connect_websocket(self, student_id: str, websocket: WebSocket):
        """Connect a WebSocket for real-time updates."""
        await websocket.accept()
        if student_id not in self.active_connections:
            self.active_connections[student_id] = []
        self.active_connections[student_id].append(websocket)

    async def disconnect_websocket(self, student_id: str, websocket: WebSocket):
        """Disconnect a WebSocket."""
        if student_id in self.active_connections:
            self.active_connections[student_id].remove(websocket)
            if not self.active_connections[student_id]:
                del self.active_connections[student_id]

    async def broadcast_update(self, student_id: str, data: Dict[str, Any]):
        """Broadcast updates to all connected WebSockets."""
        if student_id in self.active_connections:
            for connection in self.active_connections[student_id]:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    self.logger.error(f"Error broadcasting update: {str(e)}")

    async def create_activity(
        self,
        name: str,
        description: str,
        activity_type: str,
        difficulty: str,
        equipment_required: str,
        categories: List[str],
        duration_minutes: int,
        instructions: str,
        safety_notes: str,
        variations: Optional[List[str]] = None,
        modifications: Optional[Dict[str, str]] = None
    ) -> Activity:
        """Create a new physical activity."""
        try:
            # Validate inputs
            if activity_type not in self.activity_types:
                raise ValueError(f"Invalid activity type. Must be one of: {self.activity_types}")
            if difficulty not in self.difficulty_levels:
                raise ValueError(f"Invalid difficulty level. Must be one of: {self.difficulty_levels}")
            if equipment_required not in self.equipment_requirements:
                raise ValueError(f"Invalid equipment requirement. Must be one of: {self.equipment_requirements}")
            if not all(cat in self.categories for cat in categories):
                raise ValueError(f"Invalid category. Must be one of: {self.categories}")
            
            # Create activity
            activity = Activity(
                name=name,
                description=description,
                activity_type=activity_type,
                difficulty=difficulty,
                equipment_required=equipment_required,
                categories=categories,
                duration_minutes=duration_minutes,
                instructions=instructions,
                safety_notes=safety_notes,
                variations=variations or [],
                modifications=modifications or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)
            
            return activity
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating activity: {str(e)}")
            raise

    async def get_activity(self, activity_id: str) -> Optional[Activity]:
        """Retrieve an activity by ID."""
        try:
            return self.db.query(Activity).filter(Activity.id == activity_id).first()
        except Exception as e:
            self.logger.error(f"Error retrieving activity: {str(e)}")
            return None

    async def get_activities(
        self,
        activity_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        equipment_required: Optional[str] = None,
        category: Optional[str] = None,
        duration_min: Optional[int] = None,
        duration_max: Optional[int] = None
    ) -> List[Activity]:
        """Retrieve activities with optional filters."""
        try:
            query = self.db.query(Activity)
            
            if activity_type:
                query = query.filter(Activity.activity_type == activity_type)
            if difficulty:
                query = query.filter(Activity.difficulty == difficulty)
            if equipment_required:
                query = query.filter(Activity.equipment_required == equipment_required)
            if category:
                query = query.filter(Activity.categories.contains([category]))
            if duration_min is not None:
                query = query.filter(Activity.duration_minutes >= duration_min)
            if duration_max is not None:
                query = query.filter(Activity.duration_minutes <= duration_max)
            
            return query.all()
            
        except Exception as e:
            self.logger.error(f"Error retrieving activities: {str(e)}")
            return []

    async def update_activity(
        self,
        activity_id: str,
        **kwargs
    ) -> Optional[Activity]:
        """Update an existing activity."""
        try:
            activity = await self.get_activity(activity_id)
            if not activity:
                return None
            
            # Validate and update fields
            for key, value in kwargs.items():
                if hasattr(activity, key):
                    if key == "activity_type" and value not in self.activity_types:
                        raise ValueError(f"Invalid activity type: {value}")
                    if key == "difficulty" and value not in self.difficulty_levels:
                        raise ValueError(f"Invalid difficulty level: {value}")
                    if key == "equipment_required" and value not in self.equipment_requirements:
                        raise ValueError(f"Invalid equipment requirement: {value}")
                    if key == "categories" and not all(cat in self.categories for cat in value):
                        raise ValueError(f"Invalid category in: {value}")
                    
                    setattr(activity, key, value)
            
            activity.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(activity)
            
            return activity
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating activity: {str(e)}")
            return None

    async def delete_activity(self, activity_id: str) -> bool:
        """Delete an activity."""
        try:
            activity = await self.get_activity(activity_id)
            if not activity:
                return False
            
            self.db.delete(activity)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error deleting activity: {str(e)}")
            return False

    async def create_exercise(
        self,
        name: str,
        description: str,
        activity_id: str,
        sets: int,
        reps: int,
        rest_time_seconds: int,
        technique_notes: str,
        progression_steps: Optional[List[str]] = None,
        regression_steps: Optional[List[str]] = None
    ) -> Exercise:
        """Create a new exercise based on an activity."""
        try:
            activity = await self.get_activity(activity_id)
            if not activity:
                raise ValueError(f"Activity not found: {activity_id}")
            
            exercise = Exercise(
                name=name,
                description=description,
                activity_id=activity_id,
                sets=sets,
                reps=reps,
                rest_time_seconds=rest_time_seconds,
                technique_notes=technique_notes,
                progression_steps=progression_steps or [],
                regression_steps=regression_steps or [],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(exercise)
            self.db.commit()
            self.db.refresh(exercise)
            
            return exercise
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating exercise: {str(e)}")
            raise

    async def create_routine(
        self,
        name: str,
        description: str,
        class_id: str,
        activities: List[Dict[str, Any]],
        duration_minutes: int,
        warm_up_activities: Optional[List[str]] = None,
        cool_down_activities: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> Routine:
        """Create a new exercise routine."""
        try:
            # Validate class exists
            class_ = self.db.query(Class).filter(Class.id == class_id).first()
            if not class_:
                raise ValueError(f"Class not found: {class_id}")
            
            # Validate activities
            for activity_data in activities:
                activity = await self.get_activity(activity_data["activity_id"])
                if not activity:
                    raise ValueError(f"Activity not found: {activity_data['activity_id']}")
            
            routine = Routine(
                name=name,
                description=description,
                class_id=class_id,
                activities=activities,
                duration_minutes=duration_minutes,
                warm_up_activities=warm_up_activities or [],
                cool_down_activities=cool_down_activities or [],
                notes=notes or "",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(routine)
            self.db.commit()
            self.db.refresh(routine)
            
            return routine
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating routine: {str(e)}")
            raise

    async def get_routine(self, routine_id: str) -> Optional[Routine]:
        """Retrieve a routine by ID."""
        try:
            return self.db.query(Routine).filter(Routine.id == routine_id).first()
        except Exception as e:
            self.logger.error(f"Error retrieving routine: {str(e)}")
            return None

    async def get_routines(
        self,
        class_id: Optional[str] = None,
        duration_min: Optional[int] = None,
        duration_max: Optional[int] = None
    ) -> List[Routine]:
        """Retrieve routines with optional filters."""
        try:
            query = self.db.query(Routine)
            
            if class_id:
                query = query.filter(Routine.class_id == class_id)
            if duration_min is not None:
                query = query.filter(Routine.duration_minutes >= duration_min)
            if duration_max is not None:
                query = query.filter(Routine.duration_minutes <= duration_max)
            
            return query.all()
            
        except Exception as e:
            self.logger.error(f"Error retrieving routines: {str(e)}")
            return []

    async def update_routine(
        self,
        routine_id: str,
        **kwargs
    ) -> Optional[Routine]:
        """Update an existing routine."""
        try:
            routine = await self.get_routine(routine_id)
            if not routine:
                return None
            
            # Validate and update fields
            for key, value in kwargs.items():
                if hasattr(routine, key):
                    if key == "activities":
                        # Validate activities
                        for activity_data in value:
                            activity = await self.get_activity(activity_data["activity_id"])
                            if not activity:
                                raise ValueError(f"Activity not found: {activity_data['activity_id']}")
                    
                    setattr(routine, key, value)
            
            routine.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(routine)
            
            return routine
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating routine: {str(e)}")
            return None

    async def delete_routine(self, routine_id: str) -> bool:
        """Delete a routine."""
        try:
            routine = await self.get_routine(routine_id)
            if not routine:
                return False
            
            self.db.delete(routine)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error deleting routine: {str(e)}")
            return False

    async def get_activity_statistics(
        self,
        class_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get statistics about activities and routines."""
        try:
            stats = {
                "total_activities": 0,
                "activities_by_type": {},
                "activities_by_difficulty": {},
                "activities_by_equipment": {},
                "activities_by_category": {},
                "average_duration": 0,
                "total_routines": 0,
                "routines_by_class": {},
                "average_routine_duration": 0
            }
            
            # Activity statistics
            activities = await self.get_activities()
            stats["total_activities"] = len(activities)
            
            for activity in activities:
                # Count by type
                stats["activities_by_type"][activity.activity_type] = \
                    stats["activities_by_type"].get(activity.activity_type, 0) + 1
                
                # Count by difficulty
                stats["activities_by_difficulty"][activity.difficulty] = \
                    stats["activities_by_difficulty"].get(activity.difficulty, 0) + 1
                
                # Count by equipment
                stats["activities_by_equipment"][activity.equipment_required] = \
                    stats["activities_by_equipment"].get(activity.equipment_required, 0) + 1
                
                # Count by category
                for category in activity.categories:
                    stats["activities_by_category"][category] = \
                        stats["activities_by_category"].get(category, 0) + 1
                
                # Average duration
                stats["average_duration"] += activity.duration_minutes
            
            if activities:
                stats["average_duration"] /= len(activities)
            
            # Routine statistics
            routines = await self.get_routines(class_id)
            stats["total_routines"] = len(routines)
            
            for routine in routines:
                # Count by class
                stats["routines_by_class"][routine.class_id] = \
                    stats["routines_by_class"].get(routine.class_id, 0) + 1
                
                # Average routine duration
                stats["average_routine_duration"] += routine.duration_minutes
            
            if routines:
                stats["average_routine_duration"] /= len(routines)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting activity statistics: {str(e)}")
            return {}

    async def get_activity_progression(
        self,
        activity_id: str,
        student_id: str
    ) -> Dict[str, Any]:
        """Get progression data for a specific activity and student."""
        try:
            activity = await self.get_activity(activity_id)
            if not activity:
                raise ValueError(f"Activity not found: {activity_id}")
            
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError(f"Student not found: {student_id}")
            
            # Get performance history
            performance_history = self.db.query(StudentActivityPerformance).filter(
                and_(
                    StudentActivityPerformance.student_id == student_id,
                    StudentActivityPerformance.activity_id == activity_id
                )
            ).order_by(StudentActivityPerformance.date).all()
            
            # Calculate progression metrics
            progression = {
                "current_level": activity.difficulty,
                "performance_history": [],
                "improvement_rate": 0.0,
                "recommended_next_steps": []
            }
            
            if performance_history:
                # Calculate improvement rate
                first_performance = performance_history[0]
                last_performance = performance_history[-1]
                time_diff = (last_performance.date - first_performance.date).days
                if time_diff > 0:
                    improvement_rate = (last_performance.score - first_performance.score) / time_diff
                    progression["improvement_rate"] = improvement_rate
                
                # Generate performance history
                progression["performance_history"] = [
                    {
                        "date": p.date,
                        "score": p.score,
                        "notes": p.notes
                    } for p in performance_history
                ]
                
                # Generate recommendations
                if improvement_rate > 0.1:
                    progression["recommended_next_steps"].append({
                        "type": "progression",
                        "description": "Consider increasing difficulty or adding variations"
                    })
                elif improvement_rate < -0.1:
                    progression["recommended_next_steps"].append({
                        "type": "regression",
                        "description": "Consider reviewing technique or reducing difficulty"
                    })
            
            return progression
            
        except Exception as e:
            self.logger.error(f"Error getting activity progression: {str(e)}")
            raise

    async def track_activity_performance(
        self,
        activity_id: str,
        student_id: str,
        score: float,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Track performance for a specific activity and student."""
        try:
            activity = await self.get_activity(activity_id)
            if not activity:
                raise ValueError(f"Activity not found: {activity_id}")
            
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError(f"Student not found: {student_id}")
            
            # Create performance record
            performance = StudentActivityPerformance(
                student_id=student_id,
                activity_id=activity_id,
                score=score,
                notes=notes,
                date=datetime.utcnow()
            )
            
            self.db.add(performance)
            self.db.commit()
            
            # Get updated progression data
            progression = await self.get_activity_progression(activity_id, student_id)
            
            return {
                "performance": {
                    "id": performance.id,
                    "score": score,
                    "notes": notes,
                    "date": performance.date
                },
                "progression": progression
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error tracking activity performance: {str(e)}")
            raise

    async def get_recommended_activities(
        self,
        student_id: str,
        class_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recommended activities for a student based on their performance and goals."""
        try:
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError(f"Student not found: {student_id}")
            
            # Get student's performance history
            performance_history = self.db.query(StudentActivityPerformance).filter(
                StudentActivityPerformance.student_id == student_id
            ).all()
            
            # Get student's current class activities if class_id is provided
            class_activities = []
            if class_id:
                class_ = self.db.query(Class).filter(Class.id == class_id).first()
                if class_:
                    class_activities = [ra.activity for ra in class_.routines]
            
            # Calculate activity preferences and strengths
            preferences = {}
            strengths = {}
            for performance in performance_history:
                activity = await self.get_activity(performance.activity_id)
                if activity:
                    for category in activity.categories:
                        preferences[category] = preferences.get(category, 0) + performance.score
                        strengths[category] = strengths.get(category, 0) + 1
            
            # Normalize preferences and strengths
            if preferences:
                max_pref = max(preferences.values())
                preferences = {k: v/max_pref for k, v in preferences.items()}
            
            if strengths:
                max_strength = max(strengths.values())
                strengths = {k: v/max_strength for k, v in strengths.items()}
            
            # Get all available activities
            query = self.db.query(Activity)
            if class_activities:
                query = query.filter(Activity.id.notin_([a.id for a in class_activities]))
            
            activities = query.all()
            
            # Score activities based on preferences and strengths
            scored_activities = []
            for activity in activities:
                score = 0
                for category in activity.categories:
                    score += preferences.get(category, 0.5) * strengths.get(category, 0.5)
                
                scored_activities.append({
                    "activity": activity,
                    "score": score,
                    "match_reasons": [
                        f"Matches {category} preference" for category in activity.categories
                        if preferences.get(category, 0) > 0.7
                    ]
                })
            
            # Sort by score and return top recommendations
            scored_activities.sort(key=lambda x: x["score"], reverse=True)
            return scored_activities[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting recommended activities: {str(e)}")
            raise

    async def generate_activity_plan(
        self,
        student_id: str,
        class_id: str,
        duration_minutes: int,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate a personalized activity plan for a student."""
        try:
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError(f"Student not found: {student_id}")
            
            class_ = self.db.query(Class).filter(Class.id == class_id).first()
            if not class_:
                raise ValueError(f"Class not found: {class_id}")
            
            # Get recommended activities
            recommended = await self.get_recommended_activities(student_id, class_id)
            
            # Filter by focus areas if provided
            if focus_areas:
                recommended = [
                    r for r in recommended
                    if any(category in focus_areas for category in r["activity"].categories)
                ]
            
            # Create activity plan
            plan = {
                "student_id": student_id,
                "class_id": class_id,
                "duration_minutes": duration_minutes,
                "activities": [],
                "total_duration": 0
            }
            
            # Add warm-up activities
            warm_up_duration = min(10, duration_minutes // 10)
            warm_ups = [
                a for a in recommended
                if a["activity"].activity_type == ActivityType.WARM_UP
            ]
            if warm_ups:
                plan["activities"].append({
                    "activity": warm_ups[0]["activity"],
                    "duration_minutes": warm_up_duration,
                    "type": "warm_up"
                })
                plan["total_duration"] += warm_up_duration
            
            # Add main activities
            remaining_duration = duration_minutes - plan["total_duration"]
            main_activities = [
                a for a in recommended
                if a["activity"].activity_type not in [ActivityType.WARM_UP, ActivityType.COOL_DOWN]
            ]
            
            for activity in main_activities:
                if plan["total_duration"] >= duration_minutes:
                    break
                
                activity_duration = min(
                    activity["activity"].duration_minutes,
                    remaining_duration
                )
                
                plan["activities"].append({
                    "activity": activity["activity"],
                    "duration_minutes": activity_duration,
                    "type": "main"
                })
                plan["total_duration"] += activity_duration
                remaining_duration -= activity_duration
            
            # Add cool-down activities
            cool_down_duration = min(5, (duration_minutes - plan["total_duration"]))
            cool_downs = [
                a for a in recommended
                if a["activity"].activity_type == ActivityType.COOL_DOWN
            ]
            if cool_downs and cool_down_duration > 0:
                plan["activities"].append({
                    "activity": cool_downs[0]["activity"],
                    "duration_minutes": cool_down_duration,
                    "type": "cool_down"
                })
                plan["total_duration"] += cool_down_duration
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Error generating activity plan: {str(e)}")
            raise

    async def analyze_student_performance(
        self,
        student_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Analyze student's performance using the analysis manager."""
        return await self.analysis_manager.analyze_student_performance(
            student_id, start_date, end_date
        )

    async def update_student_preferences(
        self,
        student_id: str,
        activity_type: str,
        preference_score: float
    ) -> Dict[str, Any]:
        """Update student's preference for a specific activity type."""
        try:
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError(f"Student not found: {student_id}")
            
            if activity_type not in self.activity_types:
                raise ValueError(f"Invalid activity type: {activity_type}")
            
            if not 0 <= preference_score <= 1:
                raise ValueError("Preference score must be between 0 and 1")
            
            # Get or create preference
            preference = self.db.query(StudentActivityPreference).filter(
                and_(
                    StudentActivityPreference.student_id == student_id,
                    StudentActivityPreference.activity_type == activity_type
                )
            ).first()
            
            if not preference:
                preference = StudentActivityPreference(
                    student_id=student_id,
                    activity_type=activity_type,
                    preference_score=preference_score
                )
                self.db.add(preference)
            else:
                preference.preference_score = preference_score
                preference.last_updated = datetime.utcnow()
            
            self.db.commit()
            
            return {
                "student_id": student_id,
                "activity_type": activity_type,
                "preference_score": preference_score,
                "last_updated": preference.last_updated
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating student preferences: {str(e)}")
            raise

    async def create_activity_plan(
        self,
        student_id: str,
        class_id: str,
        duration_minutes: int,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a personalized activity plan for a student."""
        try:
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError(f"Student not found: {student_id}")
            
            class_ = self.db.query(Class).filter(Class.id == class_id).first()
            if not class_:
                raise ValueError(f"Class not found: {class_id}")
            
            # Generate plan using existing method
            plan_data = await self.generate_activity_plan(
                student_id=student_id,
                class_id=class_id,
                duration_minutes=duration_minutes,
                focus_areas=focus_areas
            )
            
            # Create plan record
            plan = ActivityPlan(
                student_id=student_id,
                class_id=class_id,
                duration_minutes=duration_minutes,
                focus_areas=focus_areas or []
            )
            
            self.db.add(plan)
            self.db.flush()  # Get plan ID
            
            # Create plan activities
            for i, activity_data in enumerate(plan_data["activities"]):
                plan_activity = ActivityPlanActivity(
                    plan_id=plan.id,
                    activity_id=activity_data["activity"].id,
                    order=i,
                    duration_minutes=activity_data["duration_minutes"],
                    activity_type=activity_data["type"]
                )
                self.db.add(plan_activity)
            
            self.db.commit()
            
            return {
                "plan": plan,
                "activities": plan.activities
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating activity plan: {str(e)}")
            raise

    async def track_plan_progress(
        self,
        plan_id: str,
        activity_id: str,
        is_completed: bool,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Track progress of an activity in a plan."""
        try:
            plan_activity = self.db.query(ActivityPlanActivity).filter(
                and_(
                    ActivityPlanActivity.plan_id == plan_id,
                    ActivityPlanActivity.activity_id == activity_id
                )
            ).first()
            
            if not plan_activity:
                raise ValueError(f"Activity not found in plan: {activity_id}")
            
            plan_activity.is_completed = is_completed
            if notes:
                plan_activity.notes = notes
            
            # Check if all activities are completed
            plan = self.db.query(ActivityPlan).filter(ActivityPlan.id == plan_id).first()
            if plan:
                all_completed = all(a.is_completed for a in plan.activities)
                plan.is_completed = all_completed
            
            self.db.commit()
            
            return {
                "plan_id": plan_id,
                "activity_id": activity_id,
                "is_completed": is_completed,
                "notes": notes,
                "plan_completed": plan.is_completed if plan else False
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error tracking plan progress: {str(e)}")
            raise

    async def get_student_progress_report(
        self,
        student_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive progress report for a student."""
        try:
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError(f"Student not found: {student_id}")
            
            # Get performance analysis
            performance_analysis = await self.analyze_student_performance(
                student_id=student_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Get activity progressions
            progressions = self.db.query(ActivityProgression).filter(
                ActivityProgression.student_id == student_id
            ).all()
            
            # Get completed plans
            completed_plans = self.db.query(ActivityPlan).filter(
                and_(
                    ActivityPlan.student_id == student_id,
                    ActivityPlan.is_completed == True
                )
            ).all()
            
            # Generate report
            report = {
                "student_id": student_id,
                "period": {
                    "start": start_date,
                    "end": end_date
                },
                "performance_summary": performance_analysis,
                "activity_progress": [
                    {
                        "activity_id": p.activity_id,
                        "current_level": p.current_level,
                        "improvement_rate": p.improvement_rate,
                        "last_assessment": p.last_assessment_date,
                        "next_assessment": p.next_assessment_date
                    } for p in progressions
                ],
                "completed_plans": len(completed_plans),
                "recommendations": performance_analysis["recommendations"]
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating progress report: {str(e)}")
            raise

    async def get_advanced_recommendations(
        self,
        student_id: str,
        class_id: Optional[str] = None,
        limit: int = 5,
        include_metrics: bool = True
    ) -> Dict[str, Any]:
        """Get advanced activity recommendations using multiple algorithms."""
        try:
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError(f"Student not found: {student_id}")
            
            # Get student's performance history
            performances = self.db.query(StudentActivityPerformance).filter(
                StudentActivityPerformance.student_id == student_id
            ).all()
            
            # Get student's preferences
            preferences = self.db.query(StudentActivityPreference).filter(
                StudentActivityPreference.student_id == student_id
            ).all()
            
            # Get all available activities
            query = self.db.query(Activity)
            if class_id:
                class_ = self.db.query(Class).filter(Class.id == class_id).first()
                if class_:
                    class_activities = [ra.activity for ra in class_.routines]
                    query = query.filter(Activity.id.notin_([a.id for a in class_activities]))
            
            activities = query.all()
            
            # Initialize recommendation scores
            recommendations = []
            
            for activity in activities:
                score = {
                    "activity": activity,
                    "total_score": 0.0,
                    "scores": {},
                    "match_reasons": []
                }
                
                # 1. Performance-based scoring
                performance_score = await self._calculate_performance_score(activity, performances)
                score["scores"]["performance"] = performance_score
                score["total_score"] += performance_score * 0.4
                
                # 2. Preference-based scoring
                preference_score = await self._calculate_preference_score(activity, preferences)
                score["scores"]["preference"] = preference_score
                score["total_score"] += preference_score * 0.3
                
                # 3. Difficulty progression scoring
                progression_score = await self._calculate_progression_score(activity, student_id)
                score["scores"]["progression"] = progression_score
                score["total_score"] += progression_score * 0.2
                
                # 4. Activity diversity scoring
                diversity_score = await self._calculate_diversity_score(activity, performances)
                score["scores"]["diversity"] = diversity_score
                score["total_score"] += diversity_score * 0.1
                
                # Add match reasons
                if performance_score > 0.7:
                    score["match_reasons"].append("Matches performance history")
                if preference_score > 0.7:
                    score["match_reasons"].append("Matches preferences")
                if progression_score > 0.7:
                    score["match_reasons"].append("Good progression fit")
                if diversity_score > 0.7:
                    score["match_reasons"].append("Adds activity diversity")
                
                recommendations.append(score)
            
            # Sort by total score
            recommendations.sort(key=lambda x: x["total_score"], reverse=True)
            
            result = {
                "recommendations": recommendations[:limit],
                "metrics": {}
            }
            
            if include_metrics:
                result["metrics"] = {
                    "total_activities": len(activities),
                    "scoring_weights": {
                        "performance": 0.4,
                        "preference": 0.3,
                        "progression": 0.2,
                        "diversity": 0.1
                    },
                    "score_distribution": {
                        "high": len([r for r in recommendations if r["total_score"] > 0.7]),
                        "medium": len([r for r in recommendations if 0.4 <= r["total_score"] <= 0.7]),
                        "low": len([r for r in recommendations if r["total_score"] < 0.4])
                    }
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting advanced recommendations: {str(e)}")
            raise

    async def _calculate_performance_score(
        self,
        activity: Activity,
        performances: List[StudentActivityPerformance]
    ) -> float:
        """Calculate performance-based score for an activity."""
        try:
            if not performances:
                return 0.5  # Default score for no performance history
            
            # Get relevant performances
            relevant_performances = [
                p for p in performances
                if p.activity_id == activity.id
            ]
            
            if not relevant_performances:
                return 0.5  # Default score for no specific performance history
            
            # Calculate average score
            scores = [p.score for p in relevant_performances]
            avg_score = sum(scores) / len(scores)
            
            # Calculate improvement trend
            if len(scores) > 1:
                improvement = (scores[-1] - scores[0]) / len(scores)
                trend_factor = 1 + (improvement * 0.5)  # Amplify positive trends
            else:
                trend_factor = 1.0
            
            return min(1.0, avg_score * trend_factor)
            
        except Exception as e:
            self.logger.error(f"Error calculating performance score: {str(e)}")
            return 0.5

    async def _calculate_preference_score(
        self,
        activity: Activity,
        preferences: List[StudentActivityPreference]
    ) -> float:
        """Calculate preference-based score for an activity."""
        try:
            if not preferences:
                return 0.5  # Default score for no preferences
            
            # Find matching preference
            matching_preference = next(
                (p for p in preferences if p.activity_type == activity.activity_type),
                None
            )
            
            if matching_preference:
                return matching_preference.preference_score
            
            return 0.5  # Default score for no matching preference
            
        except Exception as e:
            self.logger.error(f"Error calculating preference score: {str(e)}")
            return 0.5

    async def _calculate_progression_score(
        self,
        activity: Activity,
        student_id: str
    ) -> float:
        """Calculate progression-based score for an activity."""
        try:
            # Get student's current progression
            progression = self.db.query(ActivityProgression).filter(
                and_(
                    ActivityProgression.student_id == student_id,
                    ActivityProgression.activity_id == activity.id
                )
            ).first()
            
            if not progression:
                return 0.5  # Default score for no progression data
            
            # Calculate score based on current level and improvement rate
            level_scores = {
                DifficultyLevel.BEGINNER: 0.3,
                DifficultyLevel.INTERMEDIATE: 0.6,
                DifficultyLevel.ADVANCED: 0.9
            }
            
            base_score = level_scores.get(progression.current_level, 0.5)
            improvement_factor = 1 + (progression.improvement_rate * 0.5)
            
            return min(1.0, base_score * improvement_factor)
            
        except Exception as e:
            self.logger.error(f"Error calculating progression score: {str(e)}")
            return 0.5

    async def _calculate_diversity_score(
        self,
        activity: Activity,
        performances: List[StudentActivityPerformance]
    ) -> float:
        """Calculate diversity-based score for an activity."""
        try:
            if not performances:
                return 0.5  # Default score for no performance history
            
            # Get activity type distribution
            activity_types = {}
            for p in performances:
                activity = await self.get_activity(p.activity_id)
                if activity:
                    activity_type = activity.activity_type.value
                    activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
            
            # Calculate diversity score
            total_activities = sum(activity_types.values())
            if total_activities == 0:
                return 0.5
            
            current_type_count = activity_types.get(activity.activity_type.value, 0)
            diversity_ratio = 1 - (current_type_count / total_activities)
            
            return diversity_ratio
            
        except Exception as e:
            self.logger.error(f"Error calculating diversity score: {str(e)}")
            return 0.5

    async def get_enhanced_performance_analysis(
        self,
        student_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get enhanced performance analysis with advanced metrics."""
        try:
            # Get basic performance analysis
            basic_analysis = await self.analyze_student_performance(
                student_id=student_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Get performance records
            query = self.db.query(StudentActivityPerformance).filter(
                StudentActivityPerformance.student_id == student_id
            )
            
            if start_date:
                query = query.filter(StudentActivityPerformance.date >= start_date)
            if end_date:
                query = query.filter(StudentActivityPerformance.date <= end_date)
            
            performances = query.order_by(StudentActivityPerformance.date).all()
            
            # Initialize enhanced analysis
            enhanced_analysis = {
                **basic_analysis,
                "advanced_metrics": {
                    "consistency_score": 0.0,
                    "effort_score": 0.0,
                    "improvement_trends": {},
                    "performance_predictions": {},
                    "skill_gaps": [],
                    "opportunities": []
                }
            }
            
            if performances:
                # Calculate consistency score
                scores = [p.score for p in performances]
                enhanced_analysis["advanced_metrics"]["consistency_score"] = 1 - (np.std(scores) / np.mean(scores))
                
                # Calculate effort score (based on frequency and duration)
                total_days = (end_date - start_date).days if start_date and end_date else 30
                activity_days = len(set(p.date.date() for p in performances))
                enhanced_analysis["advanced_metrics"]["effort_score"] = activity_days / total_days
                
                # Calculate improvement trends by category
                for category in self.categories:
                    category_performances = [
                        p for p in performances
                        if any(cat == category for cat in p.activity.categories)
                    ]
                    if len(category_performances) > 1:
                        scores = [p.score for p in category_performances]
                        trend = np.polyfit(range(len(scores)), scores, 1)[0]
                        enhanced_analysis["advanced_metrics"]["improvement_trends"][category] = trend
                
                # Generate performance predictions
                for category in self.categories:
                    if category in enhanced_analysis["advanced_metrics"]["improvement_trends"]:
                        trend = enhanced_analysis["advanced_metrics"]["improvement_trends"][category]
                        current_score = enhanced_analysis["performance_by_category"][category]["average_score"]
                        predicted_score = min(1.0, current_score + (trend * 30))  # 30-day prediction
                        enhanced_analysis["advanced_metrics"]["performance_predictions"][category] = predicted_score
                
                # Identify skill gaps and opportunities
                for category in self.categories:
                    if category in enhanced_analysis["performance_by_category"]:
                        score = enhanced_analysis["performance_by_category"][category]["average_score"]
                        if score < 0.4:
                            enhanced_analysis["advanced_metrics"]["skill_gaps"].append(category)
                        elif score > 0.8:
                            enhanced_analysis["advanced_metrics"]["opportunities"].append(category)
            
            return enhanced_analysis
            
        except Exception as e:
            self.logger.error(f"Error getting enhanced performance analysis: {str(e)}")
            raise

    async def generate_progress_visualizations(self, student_id: str,
                                             start_date: Optional[datetime] = None,
                                             end_date: Optional[datetime] = None,
                                             interactive: bool = True) -> Dict[str, str]:
        """Generate progress visualizations using the visualization manager."""
        # Get performance data
        performance_data = await self._get_performance_data(student_id, start_date, end_date)
        
        # Generate visualizations
        return self.visualization_manager.generate_visualizations(
            performance_data, student_id, interactive=interactive
        )

    async def export_progress_report(self, student_id: str, format: str,
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> str:
        """Export progress report using the export manager."""
        # Get performance data
        performance_data = await self._get_performance_data(student_id, start_date, end_date)
        
        # Generate visualizations
        visualizations = self.visualization_manager.generate_visualizations(
            performance_data, student_id
        )
        
        # Export report
        return await self.export_manager.export_visualization(
            visualizations, format, student_id
        )

    async def start_collaborative_analysis(self, student_id: str,
                                         participants: List[str]) -> Dict:
        """Start a collaborative analysis session."""
        session_id = f"analysis_{student_id}_{datetime.now().isoformat()}"
        return await self.collaboration_manager.start_collaborative_session(
            session_id, participants
        )

    async def add_collaborative_annotation(self, session_id: str, user_id: str,
                                         annotation_data: dict) -> Dict:
        """Add a collaborative annotation."""
        return await self.collaboration_manager.add_annotation(
            session_id, user_id, annotation_data
        )

    async def update_collaborative_filter(self, session_id: str, user_id: str,
                                        filter_data: dict) -> Dict:
        """Update collaborative filter settings."""
        return await self.collaboration_manager.update_shared_filter(
            session_id, user_id, filter_data
        )

    async def update_collaborative_sort(self, session_id: str, user_id: str,
                                      sort_data: dict) -> Dict:
        """Update collaborative sort settings."""
        return await self.collaboration_manager.update_shared_sort(
            session_id, user_id, sort_data
        )

    async def export_collaborative_session(self, session_id: str) -> str:
        """Export collaborative session data."""
        return await self.collaboration_manager.export_session_data(session_id)

    async def cleanup_collaborative_sessions(self) -> None:
        """Clean up old collaborative sessions."""
        return await self.collaboration_manager.cleanup_old_sessions()

    async def _get_performance_data(self, student_id: str,
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve and prepare performance data."""
        try:
            # Query performance records
            query = self.db.query(StudentActivityPerformance).filter(
                StudentActivityPerformance.student_id == student_id
            )
            
            if start_date:
                query = query.filter(StudentActivityPerformance.date >= start_date)
            if end_date:
                query = query.filter(StudentActivityPerformance.date <= end_date)
            
            performances = query.all()
            
            # Convert to DataFrame
            data = []
            for performance in performances:
                activity = await self.get_activity(performance.activity_id)
                if activity:
                    data.append({
                        'date': performance.date,
                        'activity_id': performance.activity_id,
                        'activity_type': activity.activity_type.value,
                        'category': activity.categories[0] if activity.categories else 'uncategorized',
                        'score': performance.score,
                        'completed': performance.completed
                    })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            self.logger.error(f"Error retrieving performance data: {str(e)}")
            raise

    async def export_visualizations(
        self,
        student_id: str,
        visualizations: Dict[str, Any],
        format: str = 'png',
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """Export visualizations in various formats with enhanced options."""
        try:
            if format not in self.export_formats:
                raise ValueError(f"Unsupported format. Must be one of: {self.export_formats}")
            
            # Set output directory
            export_path = Path(output_dir) if output_dir else self.export_dir
            export_path = export_path / student_id
            export_path.mkdir(parents=True, exist_ok=True)
            
            exported_files = {}
            
            for name, viz in visualizations.items():
                if format == 'md':
                    # Export to Markdown
                    file_path = export_path / f"{name}.md"
                    self._export_to_markdown(viz, file_path)
                    exported_files[name] = str(file_path)
                elif format == 'tex':
                    # Export to LaTeX
                    file_path = export_path / f"{name}.tex"
                    self._export_to_latex(viz, file_path)
                    exported_files[name] = str(file_path)
                elif format == 'pptx':
                    # Export to PowerPoint
                    file_path = export_path / f"{name}.pptx"
                    self._export_to_pptx(viz, file_path)
                    exported_files[name] = str(file_path)
                elif format == 'docx':
                    # Export to Word
                    file_path = export_path / f"{name}.docx"
                    self._export_to_docx(viz, file_path)
                    exported_files[name] = str(file_path)
                elif format == 'json':
                    # Export data for interactive visualizations
                    if isinstance(viz, dict) and 'data' in viz:
                        file_path = export_path / f"{name}.json"
                        with open(file_path, 'w') as f:
                            json.dump(viz['data'], f)
                        exported_files[name] = str(file_path)
                elif format == 'xlsx':
                    # Export to Excel
                    if isinstance(viz, dict) and 'data' in viz:
                        file_path = export_path / f"{name}.xlsx"
                        self._export_to_excel(viz['data'], file_path)
                        exported_files[name] = str(file_path)
                elif format == 'csv':
                    # Export to CSV
                    if isinstance(viz, dict) and 'data' in viz:
                        file_path = export_path / f"{name}.csv"
                        self._export_to_csv(viz['data'], file_path)
                        exported_files[name] = str(file_path)
                else:
                    # Export static images
                    if isinstance(viz, str) and viz.startswith('data:image'):
                        # Convert base64 to image
                        image_data = base64.b64decode(viz.split(',')[1])
                        file_path = export_path / f"{name}.{format}"
                        with open(file_path, 'wb') as f:
                            f.write(image_data)
                        exported_files[name] = str(file_path)
                    elif isinstance(viz, dict) and 'html' in viz:
                        # Export interactive HTML
                        file_path = export_path / f"{name}.html"
                        with open(file_path, 'w') as f:
                            f.write(viz['html'])
                        exported_files[name] = str(file_path)
            
            return exported_files
            
        except Exception as e:
            self.logger.error(f"Error exporting visualizations: {str(e)}")
            raise

    def _export_to_markdown(self, visualization: Dict[str, Any], file_path: Path) -> None:
        """Export visualization to Markdown format."""
        try:
            with open(file_path, 'w') as f:
                f.write("# Activity Performance Visualization\n\n")
                
                if isinstance(visualization, dict) and 'html' in visualization:
                    f.write("## Interactive Visualization\n\n")
                    f.write("Please view in HTML format for full interactivity.\n\n")
                elif isinstance(visualization, str) and visualization.startswith('data:image'):
                    f.write("## Static Visualization\n\n")
                    f.write(f"![Visualization](data:image/png;base64,{visualization.split(',')[1]})\n\n")
                
                if isinstance(visualization, dict) and 'data' in visualization:
                    f.write("## Data Summary\n\n")
                    f.write("```json\n")
                    f.write(json.dumps(visualization['data'], indent=2))
                    f.write("\n```\n")
            
        except Exception as e:
            self.logger.error(f"Error exporting to Markdown: {str(e)}")
            raise

    def _export_to_latex(self, visualization: Dict[str, Any], file_path: Path) -> None:
        """Export visualization to LaTeX format."""
        try:
            with open(file_path, 'w') as f:
                f.write("\\documentclass{article}\n")
                f.write("\\usepackage{graphicx}\n")
                f.write("\\begin{document}\n\n")
                
                f.write("\\section{Activity Performance Visualization}\n\n")
                
                if isinstance(visualization, str) and visualization.startswith('data:image'):
                    f.write("\\begin{figure}[h]\n")
                    f.write("\\centering\n")
                    f.write("\\includegraphics[width=\\textwidth]{visualization.png}\n")
                    f.write("\\caption{Activity Performance Visualization}\n")
                    f.write("\\end{figure}\n\n")
                
                if isinstance(visualization, dict) and 'data' in visualization:
                    f.write("\\section{Data Summary}\n\n")
                    f.write("\\begin{verbatim}\n")
                    f.write(json.dumps(visualization['data'], indent=2))
                    f.write("\n\\end{verbatim}\n\n")
                
                f.write("\\end{document}\n")
            
        except Exception as e:
            self.logger.error(f"Error exporting to LaTeX: {str(e)}")
            raise

    async def _generate_chord_diagram(
        self,
        performance_by_type: Dict[str, Dict[str, Any]],
        interactive: bool = True
    ) -> Dict[str, Any]:
        """Generate chord diagram for activity relationships."""
        try:
            # Prepare data
            types = list(performance_by_type.keys())
            scores = [data["average_score"] for data in performance_by_type.values()]
            
            if interactive:
                # Create interactive chord diagram using plotly
                fig = go.Figure()
                
                # Add chord diagram
                fig.add_trace(go.Chord(
                    labels=types,
                    source=[i for i in range(len(types)) for _ in range(len(types))],
                    target=[j for _ in range(len(types)) for j in range(len(types))],
                    value=[scores[i] * scores[j] for i in range(len(types)) for j in range(len(types))]
                ))
                
                fig.update_layout(
                    title="Activity Type Relationships",
                    showlegend=False
                )
                
                return {
                    'html': fig.to_html(full_html=False),
                    'data': {
                        'types': types,
                        'scores': scores
                    }
                }
            else:
                # Create static chord diagram using matplotlib
                plt.figure(figsize=(12, 8))
                # ... static visualization code ...
                
                # Convert to base64
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
                return f"data:image/png;base64,{image_base64}"
                
        except Exception as e:
            self.logger.error(f"Error generating chord diagram: {str(e)}")
            return ""

    async def _generate_stream_graph(
        self,
        performance_history: List[Dict[str, Any]],
        interactive: bool = True
    ) -> Dict[str, Any]:
        """Generate stream graph for performance trends."""
        try:
            # Prepare data
            df = pd.DataFrame(performance_history)
            df['date'] = pd.to_datetime(df['date'])
            
            if interactive:
                # Create interactive stream graph using plotly
                fig = px.area(
                    df,
                    x='date',
                    y='score',
                    color='activity_type',
                    line_group='activity_type',
                    title="Performance Stream Graph"
                )
                
                return {
                    'html': fig.to_html(full_html=False),
                    'data': df.to_dict('records')
                }
            else:
                # Create static stream graph using matplotlib
                plt.figure(figsize=(12, 8))
                # ... static visualization code ...
                
                # Convert to base64
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
                return f"data:image/png;base64,{image_base64}"
                
        except Exception as e:
            self.logger.error(f"Error generating stream graph: {str(e)}")
            return ""

    async def _generate_heat_calendar(
        self,
        performance_history: List[Dict[str, Any]],
        interactive: bool = True
    ) -> Dict[str, Any]:
        """Generate heat calendar for performance patterns."""
        try:
            # Prepare data
            df = pd.DataFrame(performance_history)
            df['date'] = pd.to_datetime(df['date'])
            df['day'] = df['date'].dt.day
            df['month'] = df['date'].dt.month
            df['year'] = df['date'].dt.year
            
            if interactive:
                # Create interactive heat calendar using plotly
                fig = px.density_heatmap(
                    df,
                    x='day',
                    y='month',
                    z='score',
                    facet_col='year',
                    color_continuous_scale='Viridis',
                    title="Performance Heat Calendar"
                )
                
                return {
                    'html': fig.to_html(full_html=False),
                    'data': df.to_dict('records')
                }
            else:
                # Create static heat calendar using matplotlib
                plt.figure(figsize=(12, 8))
                # ... static visualization code ...
                
                # Convert to base64
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
                return f"data:image/png;base64,{image_base64}"
                
        except Exception as e:
            self.logger.error(f"Error generating heat calendar: {str(e)}")
            return ""

    async def _generate_parallel_sets(
        self,
        performance_by_category: Dict[str, Dict[str, Any]],
        interactive: bool = True
    ) -> Dict[str, Any]:
        """Generate parallel sets for category relationships."""
        try:
            # Prepare data
            categories = list(performance_by_category.keys())
            scores = [data["average_score"] for data in performance_by_category.values()]
            
            if interactive:
                # Create interactive parallel sets using plotly
                fig = go.Figure()
                
                # Add parallel sets
                fig.add_trace(go.ParallelSets(
                    dimensions=[
                        dict(label='Category', values=categories),
                        dict(label='Score', values=scores)
                    ]
                ))
                
                fig.update_layout(
                    title="Category Performance Parallel Sets"
                )
                
                return {
                    'html': fig.to_html(full_html=False),
                    'data': {
                        'categories': categories,
                        'scores': scores
                    }
                }
            else:
                # Create static parallel sets using matplotlib
                plt.figure(figsize=(12, 8))
                # ... static visualization code ...
                
                # Convert to base64
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
                return f"data:image/png;base64,{image_base64}"
                
        except Exception as e:
            self.logger.error(f"Error generating parallel sets: {str(e)}")
            return ""

    async def _generate_network_graph(
        self,
        performance_by_type: Dict[str, Dict[str, Any]],
        interactive: bool = True
    ) -> Dict[str, Any]:
        """Generate network graph for activity relationships."""
        try:
            # Prepare data
            types = list(performance_by_type.keys())
            scores = [data["average_score"] for data in performance_by_type.values()]
            
            if interactive:
                # Create interactive network graph using plotly
                fig = go.Figure()
                
                # Add nodes
                fig.add_trace(go.Scatter(
                    x=[i for i in range(len(types))],
                    y=[1] * len(types),
                    mode='markers+text',
                    marker=dict(
                        size=[score * 20 for score in scores],
                        color=scores,
                        colorscale='Viridis'
                    ),
                    text=types,
                    textposition='top center'
                ))
                
                # Add edges
                for i in range(len(types)):
                    for j in range(i + 1, len(types)):
                        fig.add_trace(go.Scatter(
                            x=[i, j],
                            y=[1, 1],
                            mode='lines',
                            line=dict(
                                width=min(scores[i], scores[j]) * 5,
                                color='rgba(128, 128, 128, 0.5)'
                            )
                        ))
                
                fig.update_layout(
                    title="Activity Type Network",
                    showlegend=False,
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                )
                
                return {
                    'html': fig.to_html(full_html=False),
                    'data': {
                        'types': types,
                        'scores': scores
                    }
                }
            else:
                # Create static network graph using networkx
                G = nx.Graph()
                for i, type_ in enumerate(types):
                    G.add_node(type_, score=scores[i])
                
                for i in range(len(types)):
                    for j in range(i + 1, len(types)):
                        G.add_edge(types[i], types[j], weight=min(scores[i], scores[j]))
                
                plt.figure(figsize=(12, 8))
                pos = nx.spring_layout(G)
                nx.draw(G, pos, with_labels=True, node_color=scores, cmap='viridis')
                
                # Convert to base64
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
                return f"data:image/png;base64,{image_base64}"
                
        except Exception as e:
            self.logger.error(f"Error generating network graph: {str(e)}")
            return ""

    async def _generate_parallel_coordinates(
        self,
        performance_by_category: Dict[str, Dict[str, Any]],
        interactive: bool = True
    ) -> Dict[str, Any]:
        """Generate parallel coordinates plot for multi-dimensional analysis."""
        try:
            # Prepare data
            categories = list(performance_by_category.keys())
            metrics = ['average_score', 'consistency', 'improvement_rate']
            
            data = []
            for category in categories:
                row = {'category': category}
                for metric in metrics:
                    row[metric] = performance_by_category[category].get(metric, 0)
                data.append(row)
            
            if interactive:
                # Create interactive parallel coordinates plot using plotly
                fig = px.parallel_coordinates(
                    data,
                    color='average_score',
                    dimensions=metrics,
                    title="Category Performance Parallel Coordinates"
                )
                
                return {
                    'html': fig.to_html(full_html=False),
                    'data': data
                }
            else:
                # Create static parallel coordinates plot using pandas
                df = pd.DataFrame(data)
                plt.figure(figsize=(12, 8))
                pd.plotting.parallel_coordinates(df, 'category')
                
                # Convert to base64
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
                return f"data:image/png;base64,{image_base64}"
                
        except Exception as e:
            self.logger.error(f"Error generating parallel coordinates: {str(e)}")
            return ""

    async def _generate_box_plot(
        self,
        performance_by_type: Dict[str, Dict[str, Any]],
        interactive: bool = True
    ) -> Dict[str, Any]:
        """Generate box plot for performance distribution."""
        try:
            # Prepare data
            types = list(performance_by_type.keys())
            scores = [data["scores"] for data in performance_by_type.values()]
            
            if interactive:
                # Create interactive box plot using plotly
                fig = go.Figure()
                
                for i, type_ in enumerate(types):
                    fig.add_trace(go.Box(
                        y=scores[i],
                        name=type_,
                        boxpoints='all',
                        jitter=0.3,
                        pointpos=-1.8
                    ))
                
                fig.update_layout(
                    title="Performance Distribution by Activity Type",
                    yaxis_title="Performance Score",
                    xaxis_title="Activity Type",
                    showlegend=False
                )
                
                return {
                    'html': fig.to_html(full_html=False),
                    'data': {
                        'types': types,
                        'scores': scores
                    }
                }
            else:
                # Create static box plot using seaborn
                plt.figure(figsize=(12, 6))
                sns.boxplot(data=scores)
                plt.xticks(range(len(types)), types, rotation=45)
                plt.title("Performance Distribution by Activity Type")
                
                # Convert to base64
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                
                return f"data:image/png;base64,{image_base64}"
                
        except Exception as e:
            self.logger.error(f"Error generating box plot: {str(e)}")
            return ""

    async def start_collaborative_session(
        self,
        student_id: str,
        session_id: str,
        websocket: WebSocket
    ) -> None:
        """Start a collaborative visualization session."""
        try:
            await websocket.accept()
            if student_id not in self.collaborative_sessions:
                self.collaborative_sessions[student_id] = {}
            
            self.collaborative_sessions[student_id][session_id] = {
                'websocket': websocket,
                'annotations': [],
                'participants': set(),
                'last_update': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"Error starting collaborative session: {str(e)}")
            raise

    async def add_collaborative_annotation(
        self,
        student_id: str,
        session_id: str,
        annotation: Dict[str, Any]
    ) -> None:
        """Add an annotation to a collaborative session."""
        try:
            if student_id in self.collaborative_sessions and session_id in self.collaborative_sessions[student_id]:
                session = self.collaborative_sessions[student_id][session_id]
                session['annotations'].append({
                    **annotation,
                    'timestamp': datetime.utcnow(),
                    'author': student_id
                })
                
                # Broadcast update to all participants
                await self._broadcast_session_update(student_id, session_id)
                
        except Exception as e:
            self.logger.error(f"Error adding collaborative annotation: {str(e)}")
            raise

    async def _broadcast_session_update(
        self,
        student_id: str,
        session_id: str
    ) -> None:
        """Broadcast updates to all participants in a collaborative session."""
        try:
            if student_id in self.collaborative_sessions and session_id in self.collaborative_sessions[student_id]:
                session = self.collaborative_sessions[student_id][session_id]
                update = {
                    'type': 'session_update',
                    'annotations': session['annotations'],
                    'timestamp': datetime.utcnow()
                }
                
                await session['websocket'].send_json(update)
                
        except Exception as e:
            self.logger.error(f"Error broadcasting session update: {str(e)}")
            raise

    async def add_real_time_update(self, student_id: str, update_type: str, data: dict):
        """Add a real-time update for a student."""
        if student_id not in self.real_time_updates:
            self.real_time_updates[student_id] = []
        
        update = {
            'timestamp': datetime.now().isoformat(),
            'type': update_type,
            'data': data
        }
        
        self.real_time_updates[student_id].append(update)
        
        # Notify subscribers
        if student_id in self.update_callbacks:
            for callback in self.update_callbacks[student_id]:
                await callback(update)
    
    async def subscribe_to_updates(self, student_id: str, callback):
        """Subscribe to real-time updates for a student."""
        if student_id not in self.update_callbacks:
            self.update_callbacks[student_id] = []
        self.update_callbacks[student_id].append(callback)
    
    async def add_annotation(self, student_id: str, visualization_id: str, annotation: dict):
        """Add a collaborative annotation to a visualization."""
        key = f"{student_id}_{visualization_id}"
        if key not in self.annotations:
            self.annotations[key] = []
        
        annotation['timestamp'] = datetime.now().isoformat()
        self.annotations[key].append(annotation)
        
        # Notify other users
        await self._notify_annotation_update(student_id, visualization_id, annotation)
    
    async def _notify_annotation_update(self, student_id: str, visualization_id: str, annotation: dict):
        """Notify users about annotation updates."""
        # Implementation for notifying other users about annotation updates
        pass
    
    async def export_visualization(self, visualization: dict, format: str, **kwargs) -> str:
        """Export visualization in various formats."""
        if format == 'latex':
            return await self._export_to_latex(visualization, **kwargs)
        elif format == 'md':
            return await self._export_to_markdown(visualization, **kwargs)
        # ... existing export formats ...
    
    async def _export_to_latex(self, visualization: dict, **kwargs) -> str:
        """Export visualization to LaTeX format."""
        doc = Document()
        
        with doc.create(Section('Student Performance Analysis')):
            doc.append(Command('centering'))
            
            # Add visualization description
            doc.append(f"Analysis of {visualization['student_id']}'s performance")
            
            # Add visualization data
            with doc.create(Subsection('Performance Metrics')):
                for metric, value in visualization['metrics'].items():
                    doc.append(f"{metric}: {value}")
            
            # Add visualization image
            if 'image_path' in visualization:
                doc.append(Command('includegraphics', options='width=0.8\\textwidth',
                                 arguments=visualization['image_path']))
        
        return doc.dumps()
    
    async def _export_to_markdown(self, visualization: dict, **kwargs) -> str:
        """Export visualization to Markdown format."""
        md = []
        
        # Add title
        md.append(f"# Performance Analysis for {visualization['student_id']}")
        
        # Add visualization description
        md.append(f"## Overview\n{visualization['description']}")
        
        # Add metrics
        md.append("## Performance Metrics")
        for metric, value in visualization['metrics'].items():
            md.append(f"- **{metric}**: {value}")
        
        # Add visualization
        if 'image_path' in visualization:
            md.append(f"![Performance Visualization]({visualization['image_path']})")
        
        return '\n'.join(md)
    
    def _generate_chord_diagram(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Generate a chord diagram showing relationships between activities."""
        # Prepare data for chord diagram
        matrix = data.pivot_table(
            values='score',
            index='activity_type',
            columns='skill_category',
            aggfunc='mean'
        ).fillna(0)
        
        # Create chord diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=list(matrix.index) + list(matrix.columns),
                color="blue"
            ),
            link=dict(
                source=[i for i in range(len(matrix.index)) for _ in range(len(matrix.columns))],
                target=[len(matrix.index) + j for _ in range(len(matrix.index)) for j in range(len(matrix.columns))],
                value=matrix.values.flatten()
            )
        )])
        
        fig.update_layout(title_text="Activity-Skill Relationships", font_size=10)
        return fig
    
    def _generate_stream_graph(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Generate a stream graph showing performance trends over time."""
        # Prepare data for stream graph
        data['date'] = pd.to_datetime(data['date'])
        data = data.set_index('date')
        
        # Create stream graph
        fig = go.Figure()
        
        for category in data['category'].unique():
            category_data = data[data['category'] == category]
            fig.add_trace(go.Scatter(
                x=category_data.index,
                y=category_data['score'],
                fill='tonexty',
                name=category,
                line=dict(width=0.5)
            ))
        
        fig.update_layout(
            title="Performance Trends Over Time",
            xaxis_title="Date",
            yaxis_title="Score",
            showlegend=True
        )
        
        return fig
    
    def _generate_parallel_coordinates(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Generate a parallel coordinates plot for multi-dimensional analysis."""
        fig = go.Figure(data=
            go.Parcoords(
                line=dict(color=data['overall_score']),
                dimensions=list([
                    dict(range=[0, 1],
                         label=col,
                         values=data[col])
                    for col in data.columns if col != 'overall_score'
                ])
            )
        )
        
        fig.update_layout(
            title="Multi-dimensional Performance Analysis",
            showlegend=True
        )
        
        return fig
    
    def _generate_network_graph(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """Generate a network graph showing activity relationships."""
        G = nx.Graph()
        
        # Add nodes and edges based on activity relationships
        for _, row in data.iterrows():
            G.add_node(row['activity'], size=row['importance'])
            for related in row['related_activities']:
                G.add_edge(row['activity'], related, weight=row['relationship_strength'])
        
        # Create network visualization
        pos = nx.spring_layout(G)
        
        edge_trace = go.Scatter(
            x=[], y=[], line=dict(width=0.5, color='#888'),
            hoverinfo='none', mode='lines')
        
        node_trace = go.Scatter(
            x=[], y=[], text=[], mode='markers+text',
            hoverinfo='text', marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                )
            )
        )
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += tuple([x0, x1, None])
            edge_trace['y'] += tuple([y0, y1, None])
        
        for node in G.nodes():
            x, y = pos[node]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['text'] += tuple([node])
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Activity Relationship Network',
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           annotations=[dict(
                               text="",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002)],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        
        return fig

    # ... rest of the existing methods ... 