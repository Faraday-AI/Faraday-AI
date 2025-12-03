"""
Specialized Widget Services
Each service handles specific widget types with focused prompts for better performance.
Supports all 39 widgets through specialized and general services.
"""

from app.services.pe.specialized_services.base_specialized_service import BaseSpecializedService
from app.services.pe.specialized_services.attendance_service import AttendanceService
from app.services.pe.specialized_services.lesson_plan_service import LessonPlanService
from app.services.pe.specialized_services.meal_plan_service import MealPlanService
from app.services.pe.specialized_services.workout_service import WorkoutService
from app.services.pe.specialized_services.sms_service import SMSService
from app.services.pe.specialized_services.general_widget_service import GeneralWidgetService
from app.services.pe.specialized_services.general_response_service import GeneralResponseService

__all__ = [
    "BaseSpecializedService",
    "AttendanceService",
    "LessonPlanService",
    "MealPlanService",
    "WorkoutService",
    "SMSService",
    "GeneralWidgetService",
    "GeneralResponseService",
]

