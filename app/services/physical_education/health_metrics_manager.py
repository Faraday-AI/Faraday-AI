from app.services.physical_education.config.model_paths import get_model_path, ensure_model_directories 
import logging
from typing import List, Dict, Optional, Union, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.metrics import track_metrics
from app.core.database import get_db
from app.models.student import (
    Student
)
from app.models.health_fitness.metrics.health import HealthMetric, HealthMetricHistory
from app.models.health_fitness.metrics.health_metrics import GeneralHealthMetricThreshold
from app.models.physical_education.pe_enums.pe_types import (
    HealthMetricType,
    HealthMetricLevel,
    HealthMetricStatus,
    HealthMetricTrigger,
    Gender,
    FitnessLevel,
    MetricType,
    MeasurementUnit
)
from sqlalchemy import and_

class HealthMetricsManager:
    """Manager for handling health metrics operations."""

    def __init__(self, db_session: Optional[Session] = None):
        self.logger = logging.getLogger("health_metrics_manager")
        self.db_session = db_session
        
        # Default thresholds for different age groups
        self.default_thresholds = {
            "5-7": {
                HealthMetricType.HEART_RATE: {"min": 70, "max": 120, "unit": MeasurementUnit.BEATS_PER_MINUTE},
                HealthMetricType.RESPIRATORY_RATE: {"min": 18, "max": 25, "unit": MeasurementUnit.BEATS_PER_MINUTE},
                HealthMetricType.FLEXIBILITY: {"min": 20, "max": 30, "unit": MeasurementUnit.CENTIMETERS},
                HealthMetricType.ENDURANCE: {"min": 3, "max": 8, "unit": MeasurementUnit.MINUTES},
            },
            "8-10": {
                HealthMetricType.HEART_RATE: {"min": 70, "max": 110, "unit": MeasurementUnit.BEATS_PER_MINUTE},
                HealthMetricType.RESPIRATORY_RATE: {"min": 17, "max": 23, "unit": MeasurementUnit.BEATS_PER_MINUTE},
                HealthMetricType.FLEXIBILITY: {"min": 22, "max": 32, "unit": MeasurementUnit.CENTIMETERS},
                HealthMetricType.ENDURANCE: {"min": 5, "max": 10, "unit": MeasurementUnit.MINUTES},
            },
            "11-13": {
                HealthMetricType.HEART_RATE: {"min": 65, "max": 105, "unit": MeasurementUnit.BEATS_PER_MINUTE},
                HealthMetricType.RESPIRATORY_RATE: {"min": 16, "max": 22, "unit": MeasurementUnit.BEATS_PER_MINUTE},
                HealthMetricType.FLEXIBILITY: {"min": 25, "max": 35, "unit": MeasurementUnit.CENTIMETERS},
                HealthMetricType.ENDURANCE: {"min": 7, "max": 12, "unit": MeasurementUnit.MINUTES},
            },
            "14-18": {
                HealthMetricType.HEART_RATE: {"min": 60, "max": 100, "unit": MeasurementUnit.BEATS_PER_MINUTE},
                HealthMetricType.RESPIRATORY_RATE: {"min": 15, "max": 20, "unit": MeasurementUnit.BEATS_PER_MINUTE},
                HealthMetricType.FLEXIBILITY: {"min": 27, "max": 37, "unit": MeasurementUnit.CENTIMETERS},
                HealthMetricType.ENDURANCE: {"min": 8, "max": 15, "unit": MeasurementUnit.MINUTES},
            }
        }

        self.metric_ranges = {
            HealthMetricType.HEIGHT: {"min": 100, "max": 200, "unit": MeasurementUnit.CENTIMETERS},
            HealthMetricType.WEIGHT: {"min": 30, "max": 150, "unit": MeasurementUnit.KILOGRAMS},
            HealthMetricType.BMI: {"min": 18.5, "max": 30, "unit": MeasurementUnit.RATIO},
            HealthMetricType.HEART_RATE: {"min": 70, "max": 120, "unit": MeasurementUnit.BEATS_PER_MINUTE},
            HealthMetricType.BLOOD_PRESSURE: {"min": 90, "max": 140, "unit": MeasurementUnit.MILLIMETERS_OF_MERCURY},
            HealthMetricType.OXYGEN_SATURATION: {"min": 95, "max": 100, "unit": MeasurementUnit.PERCENT},
            HealthMetricType.TEMPERATURE: {"min": 36.1, "max": 37.2, "unit": MeasurementUnit.CELSIUS},
            HealthMetricType.FLEXIBILITY: {"min": 20, "max": 30, "unit": MeasurementUnit.CENTIMETERS},
            HealthMetricType.STRENGTH: {"min": 0, "max": 100, "unit": MeasurementUnit.KILOGRAMS},
            HealthMetricType.ENDURANCE: {"min": 0, "max": 100, "unit": MeasurementUnit.MINUTES},
            HealthMetricType.SPEED: {"min": 0, "max": 100, "unit": MeasurementUnit.METERS_PER_SECOND},
            HealthMetricType.AGILITY: {"min": 0, "max": 100, "unit": MeasurementUnit.SECONDS},
            HealthMetricType.BALANCE: {"min": 0, "max": 100, "unit": MeasurementUnit.SECONDS},
            HealthMetricType.COORDINATION: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.REACTION_TIME: {"min": 0, "max": 1, "unit": MeasurementUnit.SECONDS},
            HealthMetricType.POWER: {"min": 0, "max": 1000, "unit": MeasurementUnit.WATTS},
            HealthMetricType.AEROBIC_CAPACITY: {"min": 0, "max": 100, "unit": MeasurementUnit.MILLILITERS_PER_KILOGRAM_PER_MINUTE},
            HealthMetricType.ANAEROBIC_CAPACITY: {"min": 0, "max": 100, "unit": MeasurementUnit.WATTS},
            HealthMetricType.MUSCULAR_ENDURANCE: {"min": 0, "max": 100, "unit": MeasurementUnit.REPETITIONS},
            HealthMetricType.MUSCULAR_STRENGTH: {"min": 0, "max": 1000, "unit": MeasurementUnit.KILOGRAMS},
            HealthMetricType.BODY_COMPOSITION: {"min": 5, "max": 30, "unit": MeasurementUnit.PERCENT},
            HealthMetricType.RESTING_HEART_RATE: {"min": 60, "max": 100, "unit": MeasurementUnit.BEATS_PER_MINUTE},
            HealthMetricType.MAXIMUM_HEART_RATE: {"min": 150, "max": 220, "unit": MeasurementUnit.BEATS_PER_MINUTE},
            HealthMetricType.RECOVERY_HEART_RATE: {"min": 0, "max": 60, "unit": MeasurementUnit.BEATS_PER_MINUTE},
            HealthMetricType.VO2_MAX: {"min": 20, "max": 80, "unit": MeasurementUnit.MILLILITERS_PER_KILOGRAM_PER_MINUTE},
            HealthMetricType.LACTATE_THRESHOLD: {"min": 2, "max": 8, "unit": MeasurementUnit.MILLIMOLES_PER_LITER},
            HealthMetricType.ANAEROBIC_THRESHOLD: {"min": 0, "max": 100, "unit": MeasurementUnit.PERCENT},
            HealthMetricType.RESTING_METABOLIC_RATE: {"min": 1200, "max": 3000, "unit": MeasurementUnit.KILOCALORIES},
            HealthMetricType.CALORIC_EXPENDITURE: {"min": 0, "max": 10000, "unit": MeasurementUnit.KILOCALORIES},
            HealthMetricType.SLEEP_QUALITY: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.STRESS_LEVEL: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.FATIGUE_LEVEL: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.PAIN_LEVEL: {"min": 0, "max": 10, "unit": MeasurementUnit.SCORE},
            HealthMetricType.MOBILITY: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.STABILITY: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.POSTURE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.MOVEMENT_QUALITY: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.SKILL_LEVEL: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.PERFORMANCE_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.PROGRESS_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.PARTICIPATION_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.ENGAGEMENT_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.MOTIVATION_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.CONFIDENCE_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.SATISFACTION_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.ENJOYMENT_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.EFFORT_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.ATTITUDE_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.BEHAVIOR_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.SOCIAL_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.EMOTIONAL_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.COGNITIVE_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.PHYSICAL_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.MENTAL_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE},
            HealthMetricType.OVERALL_SCORE: {"min": 0, "max": 100, "unit": MeasurementUnit.SCORE}
        }

    async def record_metric(
        self,
        db: Session,
        student_id: int,
        metric_type: HealthMetricType,
        value: float,
        unit: MeasurementUnit,
        notes: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> HealthMetric:
        """Record a new health metric measurement."""
        try:
            # Validate the measurement against thresholds
            is_abnormal = await self._check_abnormal(db, student_id, metric_type, value, unit)
            
            # Create new metric record
            metric = HealthMetric(
                student_id=student_id,
                metric_type=metric_type.value,
                value=value,
                unit=unit.value,
                notes=notes,
                metadata=metadata or {}
            )
            
            db.add(metric)
            db.commit()
            db.refresh(metric)
            
            # Update history if needed
            await self._update_history(db, student_id, metric_type)
            
            return metric
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error recording health metric: {str(e)}")
            raise

    @track_metrics
    async def get_metrics(
        self,
        db: Session,
        student_id: int,
        metric_type: Optional[HealthMetricType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[HealthMetric]:
        """Get health metrics for a student."""
        try:
            query = db.query(HealthMetric).filter(HealthMetric.student_id == student_id)
            
            if metric_type:
                query = query.filter(HealthMetric.metric_type == metric_type.value)
            if start_date:
                query = query.filter(HealthMetric.created_at >= start_date)
            if end_date:
                query = query.filter(HealthMetric.created_at <= end_date)
                
            return query.order_by(HealthMetric.created_at.desc()).all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving health metrics: {str(e)}")
            raise

    @track_metrics
    async def get_history(
        self,
        db: Session,
        student_id: int,
        metric_type: HealthMetricType,
        timeframe: str = "1M"  # 1D, 1W, 1M, 3M, 6M, 1Y
    ) -> List[HealthMetricHistory]:
        """Get historical health metric data."""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            if timeframe == "1D":
                start_date = end_date - timedelta(days=1)
            elif timeframe == "1W":
                start_date = end_date - timedelta(weeks=1)
            elif timeframe == "1M":
                start_date = end_date - timedelta(days=30)
            elif timeframe == "3M":
                start_date = end_date - timedelta(days=90)
            elif timeframe == "6M":
                start_date = end_date - timedelta(days=180)
            elif timeframe == "1Y":
                start_date = end_date - timedelta(days=365)
            else:
                raise ValueError(f"Invalid timeframe: {timeframe}")
            
            # Get history records
            history = db.query(HealthMetricHistory).filter(
                HealthMetricHistory.student_id == student_id,
                HealthMetricHistory.metric_type == metric_type,
                HealthMetricHistory.recorded_at >= start_date,
                HealthMetricHistory.recorded_at <= end_date
            ).order_by(HealthMetricHistory.recorded_at.desc()).all()
            
            return history
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving health metric history: {str(e)}")
            raise

    @track_metrics
    async def _check_abnormal(
        self,
        db: Session,
        student_id: int,
        metric_type: HealthMetricType,
        value: float,
        unit: MeasurementUnit
    ) -> bool:
        """Check if a metric value is abnormal based on thresholds."""
        try:
            # Get student's age group
            age_group = await self._get_student_age_group(db, student_id)
            
            # Get thresholds for the metric type and age group
            thresholds = await self._get_thresholds(db, metric_type, age_group)
            
            if not thresholds:
                return False
                
            # Convert value to threshold unit if needed
            if unit != thresholds["unit"]:
                value = self._convert_units(value, unit, thresholds["unit"])
                
            # Check if value is outside thresholds
            return value < thresholds["min"] or value > thresholds["max"]
            
        except Exception as e:
            self.logger.error(f"Error checking abnormal metric: {str(e)}")
            return False

    @track_metrics
    async def _update_history(
        self,
        db: Session,
        student_id: int,
        metric_type: HealthMetricType
    ) -> None:
        """Update the history for a metric type."""
        try:
            # Get recent metrics
            metrics = await self.get_metrics(
                db,
                student_id,
                metric_type,
                start_date=datetime.utcnow() - timedelta(days=30)
            )
            
            if not metrics:
                return
                
            # Create or update history record
            # Get the most recent metric for this type
            latest_metric = metrics[0] if metrics else None
            
            if latest_metric:
                history = HealthMetricHistory(
                    metric_id=latest_metric.id,
                    value=latest_metric.value,
                    recorded_at=datetime.utcnow(),
                    notes=f"History update for {metric_type.value}"
                )
                
                db.add(history)
                db.commit()
            
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error updating metric history: {str(e)}")
            raise

    def _calculate_variance(self, values: List[float], mean: float) -> float:
        """Calculate variance of values."""
        if not values:
            return 0.0
        squared_diff_sum = sum((x - mean) ** 2 for x in values)
        return squared_diff_sum / len(values)

    def _convert_units(
        self,
        value: float,
        from_unit: MeasurementUnit,
        to_unit: MeasurementUnit
    ) -> float:
        """Convert between different units of measurement."""
        # Implement unit conversion logic here
        # For now, assume same units
        if from_unit != to_unit:
            self.logger.warning(f"Unit conversion not implemented: {from_unit} to {to_unit}")
        return value

    async def _get_student_age_group(self, db: Session, student_id: int) -> Dict:
        """Get student's age group based on date of birth."""
        # Implement age group calculation logic here
        # For now, return default age group
        return {"age_group": "11-13"}

    async def _get_thresholds(
        self,
        db: Session,
        metric_type: HealthMetricType,
        age_group: str
    ) -> Optional[Dict]:
        """Get thresholds for a specific metric type and age group."""
        try:
            # Ensure age_group is a string
            if isinstance(age_group, dict):
                age_group = age_group.get('age_group', '11-13')
            elif not isinstance(age_group, str):
                age_group = '11-13'
            
            # First try to get custom thresholds from database
            threshold = db.query(GeneralHealthMetricThreshold).filter(
                and_(
                    GeneralHealthMetricThreshold.metric_type == metric_type.value,
                    GeneralHealthMetricThreshold.age_group == age_group
                )
            ).first()
            
            if threshold:
                return {
                    "min": threshold.min_value,
                    "max": threshold.max_value,
                    "unit": threshold.unit
                }
            
            # Fall back to default thresholds
            return self.default_thresholds.get(age_group, {}).get(metric_type)
        except Exception as e:
            self.logger.error(f"Error getting thresholds: {str(e)}")
            return None

    async def check_student_health_status(self, student_id: int) -> Dict[str, Any]:
        """Check if a student is eligible for physical activities based on health status."""
        try:
            # Get the latest health metrics for the student
            metrics = await self.get_metrics(self.db_session, student_id)
            
            # Check if any metrics are outside normal ranges
            health_issues = []
            for metric in metrics:
                if metric.metric_type in ["heart_rate", "blood_pressure"]:
                    # Check if values are within normal ranges
                    if metric.value < 60 or metric.value > 100:  # Example heart rate check
                        health_issues.append(f"Abnormal {metric.metric_type}: {metric.value}")
            
            is_eligible = len(health_issues) == 0
            
            return {
                "is_eligible": is_eligible,
                "health_issues": health_issues,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error checking student health status: {str(e)}")
            return {
                "is_eligible": True,  # Default to eligible if check fails
                "health_issues": [],
                "last_check": datetime.utcnow().isoformat()
            }

    async def start_health_monitoring(self, student_id: int, activity_id: int) -> Dict[str, Any]:
        """Start health monitoring for a student during an activity."""
        try:
            # Initialize monitoring session
            monitoring_session = {
                "student_id": student_id,
                "activity_id": activity_id,
                "start_time": datetime.utcnow(),
                "is_active": True,
                "metrics_recorded": []
            }
            
            self.logger.info(f"Started health monitoring for student {student_id} in activity {activity_id}")
            
            return {
                "monitoring_active": True,
                "session_id": f"{student_id}_{activity_id}_{int(datetime.utcnow().timestamp())}",
                "start_time": monitoring_session["start_time"].isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error starting health monitoring: {str(e)}")
            return {
                "monitoring_active": False,
                "error": str(e)
            }

    async def record_health_metric(
        self,
        student_id: int,
        metric_type: str,
        value: float
    ) -> Dict[str, Any]:
        """Record a health metric during activity."""
        try:
            # Convert string metric type to enum
            metric_enum = HealthMetricType(metric_type)
            
            # Record the metric
            metric = await self.record_metric(
                self.db_session,
                student_id,
                metric_enum,
                value,
                MeasurementUnit.BEATS_PER_MINUTE if metric_type == "heart_rate" else MeasurementUnit.SCORE
            )
            
            # Check if value is within limits
            is_within_limits = True
            if metric_type == "heart_rate":
                is_within_limits = 60 <= value <= 200  # Example range
            elif metric_type == "blood_pressure_systolic":
                is_within_limits = 90 <= value <= 140  # Example range
            elif metric_type == "blood_pressure_diastolic":
                is_within_limits = 60 <= value <= 90  # Example range
            
            return {
                "metric_recorded": True,
                "metric_id": metric.id,
                "is_within_limits": is_within_limits,
                "value": value,
                "recorded_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error recording health metric: {str(e)}")
            return {
                "metric_recorded": False,
                "is_within_limits": False,  # Default to False if recording fails
                "error": str(e)
            }

# Initialize global health metrics manager
health_metrics_manager = HealthMetricsManager() 