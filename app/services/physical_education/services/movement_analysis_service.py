from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
import json
import redis.asyncio as redis
from functools import wraps
import time
import asyncio
from fastapi import HTTPException
from prometheus_client import Counter, Histogram, Gauge

from app.core.monitoring import track_metrics
from app.services.physical_education.models.movement_analysis.movement_models import (
    MovementAnalysis,
    MovementPattern
)
from app.services.physical_education.services.movement_analyzer import MovementAnalyzer
from app.services.physical_education.services.cache_monitor import CacheMonitor
from app.services.physical_education.services.rate_limiter import RateLimiter
from app.services.physical_education.services.circuit_breaker import CircuitBreaker
from app.services.physical_education.services.activity_manager import ActivityManager
from app.services.physical_education.services.safety_manager import SafetyManager
from app.services.physical_education.services.student_manager import StudentManager
from app.services.physical_education.services.video_processor import VideoProcessor

def cache_result(ttl: int = 300):
    """Decorator to cache method results in Redis."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{':'.join(str(arg) for arg in args)}:{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
            
            # Try to get from cache
            start_time = time.time()
            cached_result = await self.redis.get(cache_key)
            
            if cached_result:
                await self.cache_monitor.track_cache_hit(func.__name__)
                await self.cache_monitor.track_cache_operation("hit", func.__name__, start_time)
                return json.loads(cached_result)
            
            # Cache miss
            await self.cache_monitor.track_cache_miss(func.__name__)
            await self.cache_monitor.track_cache_operation("miss", func.__name__, start_time)
            
            # Execute function if not in cache
            result = await func(self, *args, **kwargs)
            
            # Cache the result
            if result is not None:
                try:
                    await self.redis.set(cache_key, json.dumps(result), ex=ttl)
                    await self.cache_monitor.track_cache_operation("set", func.__name__)
                except Exception as e:
                    await self.cache_monitor.track_cache_error("set_error")
                    self.logger.error(f"Error caching result: {str(e)}")
            
            return result
        return wrapper
    return decorator

class MovementAnalysisError(Exception):
    """Base exception for movement analysis errors."""
    pass

class AnalysisTimeoutError(MovementAnalysisError):
    """Exception raised when analysis times out."""
    pass

class AnalysisOverloadError(MovementAnalysisError):
    """Exception raised when system is overloaded."""
    pass

class MovementAnalysisResult:
    """Class representing the result of a movement analysis."""
    def __init__(
        self,
        analysis_id: int,
        student_id: str,
        activity_id: int,
        movement_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        confidence_score: float,
        is_completed: bool,
        created_at: datetime,
        updated_at: datetime
    ):
        self.analysis_id = analysis_id
        self.student_id = student_id
        self.activity_id = activity_id
        self.movement_data = movement_data
        self.analysis_results = analysis_results
        self.confidence_score = confidence_score
        self.is_completed = is_completed
        self.created_at = created_at
        self.updated_at = updated_at

class MovementAnalysisMetrics:
    """Class representing metrics for movement analysis."""
    def __init__(
        self,
        total_analyses: int,
        average_confidence: float,
        completion_rate: float,
        error_rate: float,
        average_processing_time: float,
        cache_hit_rate: float,
        cache_miss_rate: float
    ):
        self.total_analyses = total_analyses
        self.average_confidence = average_confidence
        self.completion_rate = completion_rate
        self.error_rate = error_rate
        self.average_processing_time = average_processing_time
        self.cache_hit_rate = cache_hit_rate
        self.cache_miss_rate = cache_miss_rate

class MovementAnalysisService:
    """Service for managing movement analysis and storing results in the database."""
    
    # Prometheus metrics
    analysis_requests = Counter(
        'movement_analysis_requests_total',
        'Total number of movement analysis requests',
        ['operation']
    )
    analysis_duration = Histogram(
        'movement_analysis_duration_seconds',
        'Time spent processing movement analysis',
        ['operation']
    )
    analysis_errors = Counter(
        'movement_analysis_errors_total',
        'Total number of movement analysis errors',
        ['error_type']
    )
    active_analyses = Gauge(
        'movement_analysis_active',
        'Number of active movement analyses'
    )
    batch_size = Gauge(
        'movement_analysis_batch_size',
        'Current batch size for processing'
    )
    
    def __init__(self, db: Session, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.logger = logging.getLogger("movement_analysis_service")
        self.analyzer = MovementAnalyzer()
        self.cache_monitor = CacheMonitor(redis_client, "movement_analysis")
        self.rate_limiter = RateLimiter(
            rate=100,  # 100 requests per window
            burst=150,  # Allow bursts of up to 150 requests
            window=60,  # 60-second window
            logger=self.logger
        )
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            reset_timeout=60,
            half_open_timeout=30
        )
        self._batch_size = 50
        self.max_concurrent_batches = 2
        self.analysis_timeout = 30  # seconds
        self.active_analyses.set(0)
        self.batch_size.set(self._batch_size)
        self.activity_manager = ActivityManager(db)
        self.safety_manager = SafetyManager()
        self.student_manager = StudentManager()
        self.video_processor = VideoProcessor()

    async def initialize(self):
        """Initialize the movement analysis service and its dependencies."""
        try:
            await self.analyzer.initialize()
            health = await self.cache_monitor.check_cache_health()
            if not health["success"]:
                self.logger.warning(f"Cache health check failed: {health['error']}")
            
            # Initialize circuit breaker
            self.circuit_breaker = CircuitBreaker(
                failure_threshold=5,
                reset_timeout=60,
                logger=self.logger
            )
            
            self.logger.info("Movement analysis service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize service dependencies: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup service resources and its dependencies."""
        try:
            await self.analyzer.cleanup()
            await self.rate_limiter.cleanup()
            await self.circuit_breaker.cleanup()
            await self.activity_manager.cleanup()
            await self.safety_manager.cleanup()
            await self.student_manager.cleanup()
            await self.video_processor.cleanup()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
            raise

    @track_metrics
    async def create_movement_analysis(
        self,
        student_id: str,
        activity_id: int,
        movement_data: Dict[str, Any]
    ) -> MovementAnalysis:
        """Create a new movement analysis record."""
        start_time = time.time()
        self.active_analyses.inc()
        self.analysis_requests.labels(operation='create').inc()
        
        try:
            # Check rate limit
            if not await self.rate_limiter.acquire_token("create_analysis"):
                self.analysis_errors.labels(error_type='rate_limit').inc()
                raise AnalysisOverloadError("Rate limit exceeded")

            # Check circuit breaker
            if not await self.circuit_breaker.can_execute():
                self.analysis_errors.labels(error_type='circuit_breaker').inc()
                raise AnalysisOverloadError("Service temporarily unavailable")

            # Analyze the movement data with timeout
            try:
                analysis_results = await asyncio.wait_for(
                    self.analyzer.analyze(movement_data),
                    timeout=self.analysis_timeout
                )
            except asyncio.TimeoutError:
                self.analysis_errors.labels(error_type='timeout').inc()
                raise AnalysisTimeoutError("Analysis timed out")

            # Create movement analysis record
            movement_analysis = MovementAnalysis(
                student_id=student_id,
                activity_id=activity_id,
                movement_data=movement_data,
                analysis_results=analysis_results,
                confidence_score=analysis_results.get('confidence_score', 0.0),
                is_completed=True
            )
            
            self.db.add(movement_analysis)
            await self.db.flush()
            
            # Extract and store movement patterns
            patterns = await self.analyzer.extract_movement_patterns(movement_data)
            for pattern_data in patterns:
                pattern = MovementPattern(
                    analysis_id=movement_analysis.id,
                    pattern_type=pattern_data['type'],
                    pattern_data=pattern_data['data'],
                    confidence_score=pattern_data.get('confidence_score', 0.0)
                )
                self.db.add(pattern)
            
            await self.db.commit()
            await self._invalidate_caches(student_id, activity_id, movement_analysis.id)
            
            # Record success in circuit breaker
            await self.circuit_breaker.record_success()
            
            # Record metrics
            duration = time.time() - start_time
            self.analysis_duration.labels(operation='create').observe(duration)
            
            return movement_analysis
            
        except (SQLAlchemyError, AnalysisTimeoutError, AnalysisOverloadError) as e:
            await self.db.rollback()
            await self.circuit_breaker.record_failure()
            self.logger.error(f"Error creating movement analysis: {str(e)}")
            self.analysis_errors.labels(error_type='processing').inc()
            raise HTTPException(
                status_code=503 if isinstance(e, AnalysisOverloadError) else 500,
                detail=str(e)
            )
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Unexpected error creating movement analysis: {str(e)}")
            self.analysis_errors.labels(error_type='unexpected').inc()
            raise HTTPException(status_code=500, detail="Internal server error")
        finally:
            await self.rate_limiter.release_token("create_analysis")
            self.active_analyses.dec()

    async def batch_process_analyses(
        self,
        student_id: str,
        activity_id: int,
        movement_data_list: List[Dict[str, Any]]
    ) -> List[MovementAnalysis]:
        """Process multiple movement analyses in batches."""
        results = []
        semaphore = asyncio.Semaphore(self.max_concurrent_batches)
        
        async def process_batch(batch):
            async with semaphore:
                return await asyncio.gather(*[
                    self.create_movement_analysis(student_id, activity_id, data)
                    for data in batch
                ])
        
        # Process in batches
        for i in range(0, len(movement_data_list), self._batch_size):
            batch = movement_data_list[i:i + self._batch_size]
            batch_results = await process_batch(batch)
            results.extend(batch_results)
            
            # Add a small delay between batches to prevent overload
            await asyncio.sleep(0.1)
        
        return results

    @cache_result(ttl=300)
    async def get_movement_analysis(self, analysis_id: int) -> Optional[MovementAnalysis]:
        """Retrieve a movement analysis record by ID."""
        try:
            return await self.db.query(MovementAnalysis).filter(MovementAnalysis.id == analysis_id).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error retrieving movement analysis: {str(e)}")
            raise

    @cache_result(ttl=300)
    async def get_student_analyses(self, student_id: str) -> List[MovementAnalysis]:
        """Retrieve all movement analyses for a student."""
        try:
            return await self.db.query(MovementAnalysis).filter(MovementAnalysis.student_id == student_id).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error retrieving student analyses: {str(e)}")
            raise

    @cache_result(ttl=300)
    async def get_activity_analyses(self, activity_id: int) -> List[MovementAnalysis]:
        """Retrieve all movement analyses for an activity."""
        try:
            return await self.db.query(MovementAnalysis).filter(MovementAnalysis.activity_id == activity_id).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error retrieving activity analyses: {str(e)}")
            raise

    @cache_result(ttl=300)
    async def get_movement_patterns(self, analysis_id: int) -> List[MovementPattern]:
        """Retrieve all movement patterns for an analysis."""
        try:
            return await self.db.query(MovementPattern).filter(MovementPattern.analysis_id == analysis_id).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Database error retrieving movement patterns: {str(e)}")
            raise

    async def update_movement_analysis(
        self,
        analysis_id: int,
        movement_data: Optional[Dict[str, Any]] = None,
        is_completed: Optional[bool] = None
    ) -> Optional[MovementAnalysis]:
        """Update a movement analysis record."""
        try:
            analysis = await self.get_movement_analysis(analysis_id)
            if not analysis:
                return None

            if movement_data is not None:
                # Re-analyze the movement data
                analysis_results = await self.analyzer.analyze(movement_data)
                analysis.movement_data = movement_data
                analysis.analysis_results = analysis_results
                analysis.confidence_score = analysis_results.get('confidence_score', 0.0)

                # Update movement patterns
                await self.db.query(MovementPattern).filter(MovementPattern.analysis_id == analysis_id).delete()
                
                patterns = await self.analyzer.extract_movement_patterns(movement_data)
                for pattern_data in patterns:
                    pattern = MovementPattern(
                        analysis_id=analysis_id,
                        pattern_type=pattern_data['type'],
                        pattern_data=pattern_data['data'],
                        confidence_score=pattern_data.get('confidence_score', 0.0)
                    )
                    self.db.add(pattern)

            if is_completed is not None:
                analysis.is_completed = is_completed

            analysis.updated_at = datetime.utcnow()
            await self.db.commit()
            
            # Invalidate relevant caches
            await self._invalidate_caches(analysis.student_id, analysis.activity_id, analysis_id)
            
            return analysis

        except SQLAlchemyError as e:
            await self.db.rollback()
            self.logger.error(f"Database error updating movement analysis: {str(e)}")
            raise
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Error updating movement analysis: {str(e)}")
            raise

    async def delete_movement_analysis(self, analysis_id: int) -> bool:
        """Delete a movement analysis record and its patterns."""
        try:
            analysis = await self.get_movement_analysis(analysis_id)
            if not analysis:
                return False

            await self.db.delete(analysis)  # This will cascade delete patterns
            await self.db.commit()
            
            # Invalidate relevant caches
            await self._invalidate_caches(analysis.student_id, analysis.activity_id, analysis_id)
            
            return True

        except SQLAlchemyError as e:
            await self.db.rollback()
            self.logger.error(f"Database error deleting movement analysis: {str(e)}")
            raise

    @cache_result(ttl=300)
    async def get_analysis_statistics(self, student_id: str) -> Dict[str, Any]:
        """Get statistics about a student's movement analyses."""
        try:
            analyses = await self.get_student_analyses(student_id)
            
            total_analyses = len(analyses)
            avg_confidence = sum(a.confidence_score for a in analyses) / total_analyses if total_analyses > 0 else 0
            completed_analyses = sum(1 for a in analyses if a.is_completed)
            
            return {
                "total_analyses": total_analyses,
                "completed_analyses": completed_analyses,
                "average_confidence_score": avg_confidence,
                "last_analysis_date": max(a.created_at for a in analyses) if analyses else None
            }

        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting analysis statistics: {str(e)}")
            raise

    async def _invalidate_caches(self, student_id: str, activity_id: int, analysis_id: int):
        """Invalidate relevant cache entries."""
        try:
            cache_keys = [
                f"get_movement_analysis:{analysis_id}",
                f"get_student_analyses:{student_id}",
                f"get_activity_analyses:{activity_id}",
                f"get_movement_patterns:{analysis_id}",
                f"get_analysis_statistics:{student_id}"
            ]
            
            for key in cache_keys:
                await self.redis.delete(key)
                await self.cache_monitor.track_cache_operation("delete", "invalidation")
                
        except Exception as e:
            await self.cache_monitor.track_cache_error("invalidation_error")
            self.logger.error(f"Error invalidating caches: {str(e)}")

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for the service."""
        return await self.cache_monitor.get_cache_stats()

    async def check_cache_health(self) -> Dict[str, Any]:
        """Check the health of the cache system."""
        return await self.cache_monitor.check_cache_health()

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            'active_analyses': self.active_analyses._value.get(),
            'batch_size': self.batch_size._value.get(),
            'circuit_breaker_state': await self.circuit_breaker.get_state(),
            'rate_limiter_stats': await self.rate_limiter.get_usage_stats(),
            'cache_stats': await self.cache_monitor.get_cache_stats(),
            'error_counts': {
                'rate_limit': self.analysis_errors._metrics['movement_analysis_errors_total']._samples[0].value,
                'circuit_breaker': self.analysis_errors._metrics['movement_analysis_errors_total']._samples[1].value,
                'timeout': self.analysis_errors._metrics['movement_analysis_errors_total']._samples[2].value,
                'processing': self.analysis_errors._metrics['movement_analysis_errors_total']._samples[3].value,
                'unexpected': self.analysis_errors._metrics['movement_analysis_errors_total']._samples[4].value
            }
        }

    async def analyze_activity_movements(
        self,
        activity_id: int,
        student_id: str,
        video_data: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Analyze movements for a specific activity with video processing."""
        try:
            # Get activity details
            activity = await self.activity_manager.get_activity(activity_id)
            if not activity:
                raise HTTPException(status_code=404, detail="Activity not found")

            # Process video if provided
            if video_data:
                processed_data = await self.video_processor.process_movement_data(video_data)
                movement_data = processed_data.get('movement_data', {})
            else:
                movement_data = {}

            # Perform movement analysis
            analysis = await self.create_movement_analysis(
                student_id=student_id,
                activity_id=activity_id,
                movement_data=movement_data
            )

            # Check for safety concerns
            safety_assessment = await self.safety_manager.assess_movement_safety(
                movement_data=movement_data,
                activity_type=activity.activity_type
            )

            # Update student progress
            await self.student_manager.update_movement_progress(
                student_id=student_id,
                activity_id=activity_id,
                analysis_id=analysis.id,
                safety_assessment=safety_assessment
            )

            return {
                'analysis': analysis,
                'safety_assessment': safety_assessment,
                'activity_details': activity
            }

        except Exception as e:
            self.logger.error(f"Error analyzing activity movements: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_student_progress(
        self,
        student_id: str,
        activity_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive progress report for a student."""
        try:
            # Get all analyses for the student
            analyses = await self.get_student_analyses(student_id)
            
            # Filter by activity type if specified
            if activity_type:
                analyses = [a for a in analyses if a.activity.activity_type == activity_type]

            # Calculate progress metrics
            total_analyses = len(analyses)
            completed_analyses = sum(1 for a in analyses if a.is_completed)
            avg_confidence = sum(a.confidence_score for a in analyses) / total_analyses if total_analyses > 0 else 0

            # Get safety assessments
            safety_metrics = await self.safety_manager.get_student_safety_metrics(student_id)

            # Get activity-specific progress
            activity_progress = await self.activity_manager.get_student_activity_progress(student_id)

            return {
                'total_analyses': total_analyses,
                'completed_analyses': completed_analyses,
                'average_confidence': avg_confidence,
                'safety_metrics': safety_metrics,
                'activity_progress': activity_progress,
                'last_analysis_date': max(a.created_at for a in analyses) if analyses else None
            }

        except Exception as e:
            self.logger.error(f"Error getting student progress: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def assess_movement_risks(
        self,
        movement_data: Dict[str, Any],
        activity_type: str
    ) -> Dict[str, Any]:
        """Assess potential risks in movement patterns."""
        try:
            # Get safety guidelines for the activity type
            safety_guidelines = await self.safety_manager.get_activity_safety_guidelines(activity_type)

            # Analyze movement patterns
            patterns = await self.analyzer.extract_movement_patterns(movement_data)

            # Assess risks for each pattern
            risk_assessments = []
            for pattern in patterns:
                risk_assessment = await self.safety_manager.assess_movement_risk(
                    pattern=pattern,
                    guidelines=safety_guidelines
                )
                risk_assessments.append(risk_assessment)

            # Generate safety recommendations
            recommendations = await self.safety_manager.generate_safety_recommendations(
                risk_assessments=risk_assessments,
                activity_type=activity_type
            )

            return {
                'risk_assessments': risk_assessments,
                'recommendations': recommendations,
                'safety_guidelines': safety_guidelines
            }

        except Exception as e:
            self.logger.error(f"Error assessing movement risks: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 