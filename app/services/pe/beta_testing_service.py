"""
Beta Testing Infrastructure Service
Handles beta testing, feedback collection, and usage analytics for the teacher system
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
import uuid
import json

from app.models.beta_testing import (
    BetaTestingParticipant,
    BetaTestingProgram,
    BetaTestingFeedback,
    BetaTestingSurvey,
    BetaTestingSurveyResponse,
    BetaTestingUsageAnalytics,
    BetaTestingFeatureFlag,
    BetaTestingNotification,
    BetaTestingReport
)
from app.schemas.beta_testing import (
    BetaTestingParticipantCreate,
    BetaTestingParticipantUpdate,
    BetaTestingParticipantResponse,
    BetaTestingProgramCreate,
    BetaTestingProgramUpdate,
    BetaTestingProgramResponse,
    BetaTestingFeedbackCreate,
    BetaTestingFeedbackUpdate,
    BetaTestingFeedbackResponse,
    BetaTestingSurveyCreate,
    BetaTestingSurveyResponse,
    BetaTestingSurveyResponseCreate,
    BetaTestingSurveyResponseResponse,
    BetaTestingUsageAnalyticsResponse,
    BetaTestingFeatureFlagCreate,
    BetaTestingFeatureFlagUpdate,
    BetaTestingFeatureFlagResponse,
    BetaTestingNotificationResponse,
    BetaTestingReportCreate,
    BetaTestingReportResponse,
    BetaTestingDashboardSummary,
    BetaTestingAnalyticsSummary
)


class BetaTestingService:
    def __init__(self, db: Session):
        self.db = db

    # ==================== PARTICIPANT MANAGEMENT ====================
    
    def enroll_participant(
        self, 
        teacher_id: str, 
        program_id: str, 
        participant_data: BetaTestingParticipantCreate
    ) -> BetaTestingParticipantResponse:
        """Enroll a teacher in a beta testing program"""
        try:
            # Check if program exists and has capacity
            program = self.db.query(BetaTestingProgram).filter(
                BetaTestingProgram.id == program_id
            ).first()
            
            if not program:
                raise Exception("Beta testing program not found")
            
            if program.current_participants >= program.max_participants:
                raise Exception("Beta testing program is at capacity")
            
            # Check if teacher is already enrolled
            existing = self.db.query(BetaTestingParticipant).filter(
                and_(
                    BetaTestingParticipant.teacher_id == teacher_id,
                    BetaTestingParticipant.beta_program_id == program_id
                )
            ).first()
            
            if existing:
                raise Exception("Teacher is already enrolled in this program")
            
            participant = BetaTestingParticipant(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                beta_program_id=program_id,
                testing_phase=participant_data.testing_phase,
                assigned_features=participant_data.assigned_features,
                testing_goals=participant_data.testing_goals,
                contact_preferences=participant_data.contact_preferences,
                consent_given=participant_data.consent_given,
                consent_date=datetime.utcnow() if participant_data.consent_given else None
            )
            
            self.db.add(participant)
            
            # Update program participant count
            program.current_participants += 1
            
            self.db.commit()
            
            return self._participant_to_response(participant)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to enroll participant: {str(e)}")

    def get_participant(
        self, 
        participant_id: str, 
        teacher_id: str
    ) -> Optional[BetaTestingParticipantResponse]:
        """Get a specific participant"""
        participant = self.db.query(BetaTestingParticipant).filter(
            and_(
                BetaTestingParticipant.id == participant_id,
                BetaTestingParticipant.teacher_id == teacher_id
            )
        ).first()
        
        return self._participant_to_response(participant) if participant else None

    def get_teacher_participations(
        self, 
        teacher_id: str
    ) -> List[BetaTestingParticipantResponse]:
        """Get all beta testing participations for a teacher"""
        participants = self.db.query(BetaTestingParticipant).filter(
            BetaTestingParticipant.teacher_id == teacher_id
        ).order_by(desc(BetaTestingParticipant.enrollment_date)).all()
        
        return [self._participant_to_response(participant) for participant in participants]

    def update_participant_status(
        self, 
        participant_id: str, 
        teacher_id: str, 
        status: str
    ) -> Optional[BetaTestingParticipantResponse]:
        """Update participant status"""
        participant = self.db.query(BetaTestingParticipant).filter(
            and_(
                BetaTestingParticipant.id == participant_id,
                BetaTestingParticipant.teacher_id == teacher_id
            )
        ).first()
        
        if not participant:
            return None
        
        participant.status = status
        
        if status == "withdrawn":
            participant.withdrawal_date = datetime.utcnow()
        elif status == "completed":
            participant.completion_date = datetime.utcnow()
        
        participant.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._participant_to_response(participant)

    # ==================== PROGRAM MANAGEMENT ====================
    
    def create_program(
        self, 
        program_data: BetaTestingProgramCreate
    ) -> BetaTestingProgramResponse:
        """Create a new beta testing program"""
        try:
            program = BetaTestingProgram(
                id=str(uuid.uuid4()),
                program_name=program_data.program_name,
                program_description=program_data.program_description,
                program_type=program_data.program_type,
                target_audience=program_data.target_audience,
                max_participants=program_data.max_participants,
                start_date=program_data.start_date,
                end_date=program_data.end_date,
                success_criteria=program_data.success_criteria,
                metrics_to_track=program_data.metrics_to_track
            )
            
            self.db.add(program)
            self.db.commit()
            
            return self._program_to_response(program)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create beta testing program: {str(e)}")

    def get_active_programs(
        self, 
        target_audience: Optional[str] = None
    ) -> List[BetaTestingProgramResponse]:
        """Get active beta testing programs"""
        query = self.db.query(BetaTestingProgram).filter(
            and_(
                BetaTestingProgram.is_active == True,
                BetaTestingProgram.start_date <= datetime.utcnow(),
                BetaTestingProgram.end_date >= datetime.utcnow()
            )
        )
        
        if target_audience:
            query = query.filter(
                or_(
                    BetaTestingProgram.target_audience == target_audience,
                    BetaTestingProgram.target_audience == "all_teachers"
                )
            )
        
        programs = query.order_by(asc(BetaTestingProgram.start_date)).all()
        
        return [self._program_to_response(program) for program in programs]

    def get_program_participants(
        self, 
        program_id: str, 
        status: Optional[str] = None
    ) -> List[BetaTestingParticipantResponse]:
        """Get participants for a program"""
        query = self.db.query(BetaTestingParticipant).filter(
            BetaTestingParticipant.beta_program_id == program_id
        )
        
        if status:
            query = query.filter(BetaTestingParticipant.status == status)
        
        participants = query.order_by(asc(BetaTestingParticipant.enrollment_date)).all()
        
        return [self._participant_to_response(participant) for participant in participants]

    # ==================== FEEDBACK MANAGEMENT ====================
    
    def submit_feedback(
        self, 
        participant_id: str, 
        teacher_id: str, 
        feedback_data: BetaTestingFeedbackCreate
    ) -> BetaTestingFeedbackResponse:
        """Submit feedback for a beta testing feature"""
        try:
            # Verify participant ownership
            participant = self.db.query(BetaTestingParticipant).filter(
                and_(
                    BetaTestingParticipant.id == participant_id,
                    BetaTestingParticipant.teacher_id == teacher_id
                )
            ).first()
            
            if not participant:
                raise Exception("Participant not found or access denied")
            
            feedback = BetaTestingFeedback(
                id=str(uuid.uuid4()),
                participant_id=participant_id,
                feedback_type=feedback_data.feedback_type,
                feature_name=feedback_data.feature_name,
                feedback_title=feedback_data.feedback_title,
                feedback_description=feedback_data.feedback_description,
                severity_level=feedback_data.severity_level,
                priority_level=feedback_data.priority_level,
                user_impact=feedback_data.user_impact,
                reproduction_steps=feedback_data.reproduction_steps,
                expected_behavior=feedback_data.expected_behavior,
                actual_behavior=feedback_data.actual_behavior,
                browser_info=feedback_data.browser_info,
                device_info=feedback_data.device_info,
                screen_resolution=feedback_data.screen_resolution,
                operating_system=feedback_data.operating_system,
                additional_context=feedback_data.additional_context
            )
            
            self.db.add(feedback)
            self.db.commit()
            
            return self._feedback_to_response(feedback)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to submit feedback: {str(e)}")

    def get_participant_feedback(
        self, 
        participant_id: str, 
        teacher_id: str,
        feedback_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[BetaTestingFeedbackResponse]:
        """Get feedback for a participant"""
        # Verify participant ownership
        participant = self.db.query(BetaTestingParticipant).filter(
            and_(
                BetaTestingParticipant.id == participant_id,
                BetaTestingParticipant.teacher_id == teacher_id
            )
        ).first()
        
        if not participant:
            return []
        
        query = self.db.query(BetaTestingFeedback).filter(
            BetaTestingFeedback.participant_id == participant_id
        )
        
        if feedback_type:
            query = query.filter(BetaTestingFeedback.feedback_type == feedback_type)
        
        feedback = query.order_by(desc(BetaTestingFeedback.created_at)).offset(offset).limit(limit).all()
        
        return [self._feedback_to_response(f) for f in feedback]

    def resolve_feedback(
        self, 
        feedback_id: str, 
        resolution_notes: str,
        resolved_by: str
    ) -> Optional[BetaTestingFeedbackResponse]:
        """Resolve feedback item"""
        feedback = self.db.query(BetaTestingFeedback).filter(
            BetaTestingFeedback.id == feedback_id
        ).first()
        
        if not feedback:
            return None
        
        feedback.is_resolved = True
        feedback.resolution_notes = resolution_notes
        feedback.resolved_at = datetime.utcnow()
        feedback.resolved_by = resolved_by
        feedback.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return self._feedback_to_response(feedback)

    # ==================== SURVEY MANAGEMENT ====================
    
    def get_available_surveys(
        self, 
        participant_id: str, 
        teacher_id: str
    ) -> List[BetaTestingSurveyResponse]:
        """Get available surveys for a participant"""
        # Verify participant ownership
        participant = self.db.query(BetaTestingParticipant).filter(
            and_(
                BetaTestingParticipant.id == participant_id,
                BetaTestingParticipant.teacher_id == teacher_id
            )
        ).first()
        
        if not participant:
            return []
        
        # Get surveys for the participant's program
        surveys = self.db.query(BetaTestingSurvey).filter(
            and_(
                BetaTestingSurvey.program_id == participant.beta_program_id,
                BetaTestingSurvey.is_active == True,
                BetaTestingSurvey.start_date <= datetime.utcnow(),
                BetaTestingSurvey.end_date >= datetime.utcnow()
            )
        ).order_by(asc(BetaTestingSurvey.start_date)).all()
        
        return [self._survey_to_response(survey) for survey in surveys]

    def submit_survey_response(
        self, 
        participant_id: str, 
        teacher_id: str, 
        survey_id: str, 
        response_data: BetaTestingSurveyResponseCreate
    ) -> BetaTestingSurveyResponseResponse:
        """Submit survey response"""
        try:
            # Verify participant ownership
            participant = self.db.query(BetaTestingParticipant).filter(
                and_(
                    BetaTestingParticipant.id == participant_id,
                    BetaTestingParticipant.teacher_id == teacher_id
                )
            ).first()
            
            if not participant:
                raise Exception("Participant not found or access denied")
            
            # Check if response already exists
            existing = self.db.query(BetaTestingSurveyResponse).filter(
                and_(
                    BetaTestingSurveyResponse.participant_id == participant_id,
                    BetaTestingSurveyResponse.survey_id == survey_id
                )
            ).first()
            
            if existing:
                # Update existing response
                existing.response_data = response_data.response_data
                existing.completion_percentage = response_data.completion_percentage
                existing.time_spent_minutes = response_data.time_spent_minutes
                existing.is_completed = response_data.is_completed
                if response_data.is_completed:
                    existing.submitted_at = datetime.utcnow()
                
                self.db.commit()
                return self._survey_response_to_response(existing)
            
            # Create new response
            response = BetaTestingSurveyResponse(
                id=str(uuid.uuid4()),
                participant_id=participant_id,
                survey_id=survey_id,
                response_data=response_data.response_data,
                completion_percentage=response_data.completion_percentage,
                time_spent_minutes=response_data.time_spent_minutes,
                is_completed=response_data.is_completed,
                submitted_at=datetime.utcnow() if response_data.is_completed else None
            )
            
            self.db.add(response)
            self.db.commit()
            
            return self._survey_response_to_response(response)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to submit survey response: {str(e)}")

    # ==================== USAGE ANALYTICS ====================
    
    def track_feature_usage(
        self, 
        participant_id: str, 
        feature_name: str,
        session_count: int = 1,
        time_minutes: int = 0,
        interactions: int = 0,
        errors: int = 0,
        satisfaction_score: Optional[float] = None,
        performance_metrics: Optional[Dict[str, Any]] = None
    ) -> BetaTestingUsageAnalyticsResponse:
        """Track feature usage for analytics"""
        try:
            # Check if analytics already exist for today
            today = date.today()
            existing = self.db.query(BetaTestingUsageAnalytics).filter(
                and_(
                    BetaTestingUsageAnalytics.participant_id == participant_id,
                    BetaTestingUsageAnalytics.feature_name == feature_name,
                    BetaTestingUsageAnalytics.usage_date == today
                )
            ).first()
            
            if existing:
                # Update existing analytics
                existing.session_count += session_count
                existing.total_time_minutes += time_minutes
                existing.feature_interactions += interactions
                existing.error_count += errors
                if satisfaction_score:
                    existing.user_satisfaction_score = satisfaction_score
                if performance_metrics:
                    existing.performance_metrics = performance_metrics
                
                # Calculate success rate
                total_attempts = existing.feature_interactions + existing.error_count
                if total_attempts > 0:
                    existing.success_rate = ((existing.feature_interactions / total_attempts) * 100)
            else:
                # Create new analytics
                success_rate = 100.0
                if interactions + errors > 0:
                    success_rate = ((interactions / (interactions + errors)) * 100)
                
                existing = BetaTestingUsageAnalytics(
                    id=str(uuid.uuid4()),
                    participant_id=participant_id,
                    feature_name=feature_name,
                    session_count=session_count,
                    total_time_minutes=time_minutes,
                    feature_interactions=interactions,
                    error_count=errors,
                    success_rate=success_rate,
                    user_satisfaction_score=satisfaction_score,
                    performance_metrics=performance_metrics or {}
                )
                
                self.db.add(existing)
            
            self.db.commit()
            
            return self._usage_analytics_to_response(existing)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to track feature usage: {str(e)}")

    def get_participant_analytics(
        self, 
        participant_id: str, 
        teacher_id: str,
        days: int = 30
    ) -> List[BetaTestingUsageAnalyticsResponse]:
        """Get usage analytics for a participant"""
        # Verify participant ownership
        participant = self.db.query(BetaTestingParticipant).filter(
            and_(
                BetaTestingParticipant.id == participant_id,
                BetaTestingParticipant.teacher_id == teacher_id
            )
        ).first()
        
        if not participant:
            return []
        
        start_date = date.today() - timedelta(days=days)
        
        analytics = self.db.query(BetaTestingUsageAnalytics).filter(
            and_(
                BetaTestingUsageAnalytics.participant_id == participant_id,
                BetaTestingUsageAnalytics.usage_date >= start_date
            )
        ).order_by(desc(BetaTestingUsageAnalytics.usage_date)).all()
        
        return [self._usage_analytics_to_response(stat) for stat in analytics]

    # ==================== FEATURE FLAGS ====================
    
    def get_feature_flags(
        self, 
        target_audience: str
    ) -> List[BetaTestingFeatureFlagResponse]:
        """Get feature flags for a target audience"""
        flags = self.db.query(BetaTestingFeatureFlag).filter(
            and_(
                BetaTestingFeatureFlag.is_enabled == True,
                or_(
                    BetaTestingFeatureFlag.target_audience == target_audience,
                    BetaTestingFeatureFlag.target_audience == "all_teachers"
                )
            )
        ).order_by(asc(BetaTestingFeatureFlag.feature_name)).all()
        
        return [self._feature_flag_to_response(flag) for flag in flags]

    def is_feature_enabled(
        self, 
        feature_name: str, 
        teacher_id: str
    ) -> bool:
        """Check if a feature is enabled for a teacher"""
        # Get teacher's target audience (simplified - would need actual teacher data)
        target_audience = "pe_teachers"  # Default for now
        
        flag = self.db.query(BetaTestingFeatureFlag).filter(
            and_(
                BetaTestingFeatureFlag.feature_name == feature_name,
                BetaTestingFeatureFlag.is_enabled == True,
                or_(
                    BetaTestingFeatureFlag.target_audience == target_audience,
                    BetaTestingFeatureFlag.target_audience == "all_teachers"
                )
            )
        ).first()
        
        if not flag:
            return False
        
        # Check rollout percentage
        if flag.rollout_percentage < 100:
            # Simple hash-based rollout (would need more sophisticated logic)
            teacher_hash = hash(teacher_id) % 100
            return teacher_hash < flag.rollout_percentage
        
        return True

    # ==================== NOTIFICATIONS ====================
    
    def get_participant_notifications(
        self, 
        participant_id: str, 
        teacher_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[BetaTestingNotificationResponse]:
        """Get notifications for a participant"""
        # Verify participant ownership
        participant = self.db.query(BetaTestingParticipant).filter(
            and_(
                BetaTestingParticipant.id == participant_id,
                BetaTestingParticipant.teacher_id == teacher_id
            )
        ).first()
        
        if not participant:
            return []
        
        query = self.db.query(BetaTestingNotification).filter(
            BetaTestingNotification.participant_id == participant_id
        )
        
        if unread_only:
            query = query.filter(BetaTestingNotification.is_read == False)
        
        # Filter out expired notifications
        query = query.filter(
            or_(
                BetaTestingNotification.expires_at.is_(None),
                BetaTestingNotification.expires_at > datetime.utcnow()
            )
        )
        
        notifications = query.order_by(desc(BetaTestingNotification.priority_level), desc(BetaTestingNotification.created_at)).offset(offset).limit(limit).all()
        
        return [self._notification_to_response(notification) for notification in notifications]

    def mark_notification_as_read(
        self, 
        notification_id: str, 
        participant_id: str, 
        teacher_id: str
    ) -> bool:
        """Mark a notification as read"""
        # Verify participant ownership
        participant = self.db.query(BetaTestingParticipant).filter(
            and_(
                BetaTestingParticipant.id == participant_id,
                BetaTestingParticipant.teacher_id == teacher_id
            )
        ).first()
        
        if not participant:
            return False
        
        notification = self.db.query(BetaTestingNotification).filter(
            and_(
                BetaTestingNotification.id == notification_id,
                BetaTestingNotification.participant_id == participant_id
            )
        ).first()
        
        if not notification:
            return False
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        self.db.commit()
        
        return True

    # ==================== DASHBOARD & ANALYTICS ====================
    
    def get_dashboard_summary(
        self, 
        teacher_id: str
    ) -> BetaTestingDashboardSummary:
        """Get dashboard summary for a teacher"""
        # Get participations
        participations = self.get_teacher_participations(teacher_id)
        
        # Get active participations
        active_participations = [p for p in participations if p.status == "active"]
        
        # Get recent feedback count
        recent_feedback_count = 0
        for participation in active_participations:
            feedback = self.get_participant_feedback(participation.id, teacher_id, limit=1000)
            recent_feedback = [f for f in feedback if f.created_at >= datetime.utcnow() - timedelta(days=7)]
            recent_feedback_count += len(recent_feedback)
        
        # Get unread notifications count
        unread_notifications = 0
        for participation in active_participations:
            notifications = self.get_participant_notifications(participation.id, teacher_id, unread_only=True, limit=1000)
            unread_notifications += len(notifications)
        
        # Get pending surveys count
        pending_surveys = 0
        for participation in active_participations:
            surveys = self.get_available_surveys(participation.id, teacher_id)
            pending_surveys += len(surveys)
        
        return BetaTestingDashboardSummary(
            total_participations=len(participations),
            active_participations=len(active_participations),
            recent_feedback_count=recent_feedback_count,
            unread_notifications=unread_notifications,
            pending_surveys=pending_surveys,
            last_activity=self._get_last_activity(teacher_id)
        )

    def get_analytics_summary(
        self, 
        program_id: str
    ) -> BetaTestingAnalyticsSummary:
        """Get analytics summary for a program"""
        # Get program participants
        participants = self.get_program_participants(program_id)
        
        # Get feedback statistics
        total_feedback = 0
        resolved_feedback = 0
        for participant in participants:
            feedback = self.db.query(BetaTestingFeedback).filter(
                BetaTestingFeedback.participant_id == participant.id
            ).all()
            total_feedback += len(feedback)
            resolved_feedback += len([f for f in feedback if f.is_resolved])
        
        # Get survey completion rate
        total_surveys = 0
        completed_surveys = 0
        for participant in participants:
            responses = self.db.query(BetaTestingSurveyResponse).filter(
                BetaTestingSurveyResponse.participant_id == participant.id
            ).all()
            total_surveys += len(responses)
            completed_surveys += len([r for r in responses if r.is_completed])
        
        # Get usage statistics
        total_sessions = 0
        total_time_minutes = 0
        for participant in participants:
            analytics = self.db.query(BetaTestingUsageAnalytics).filter(
                BetaTestingUsageAnalytics.participant_id == participant.id
            ).all()
            total_sessions += sum(a.session_count for a in analytics)
            total_time_minutes += sum(a.total_time_minutes for a in analytics)
        
        return BetaTestingAnalyticsSummary(
            total_participants=len(participants),
            active_participants=len([p for p in participants if p.status == "active"]),
            total_feedback=total_feedback,
            resolved_feedback=resolved_feedback,
            feedback_resolution_rate=(resolved_feedback / total_feedback * 100) if total_feedback > 0 else 0,
            total_surveys=total_surveys,
            completed_surveys=completed_surveys,
            survey_completion_rate=(completed_surveys / total_surveys * 100) if total_surveys > 0 else 0,
            total_sessions=total_sessions,
            total_time_minutes=total_time_minutes,
            average_session_time=total_time_minutes / total_sessions if total_sessions > 0 else 0
        )

    # ==================== HELPER METHODS ====================
    
    def _get_last_activity(self, teacher_id: str) -> Optional[datetime]:
        """Get last activity timestamp for a teacher"""
        # Get last feedback
        last_feedback = self.db.query(BetaTestingFeedback).join(BetaTestingParticipant).filter(
            BetaTestingParticipant.teacher_id == teacher_id
        ).order_by(desc(BetaTestingFeedback.created_at)).first()
        
        # Get last survey response
        last_survey = self.db.query(BetaTestingSurveyResponse).join(BetaTestingParticipant).filter(
            BetaTestingParticipant.teacher_id == teacher_id
        ).order_by(desc(BetaTestingSurveyResponse.submitted_at)).first()
        
        # Get last usage analytics
        last_usage = self.db.query(BetaTestingUsageAnalytics).join(BetaTestingParticipant).filter(
            BetaTestingParticipant.teacher_id == teacher_id
        ).order_by(desc(BetaTestingUsageAnalytics.created_at)).first()
        
        timestamps = []
        if last_feedback:
            timestamps.append(last_feedback.created_at)
        if last_survey and last_survey.submitted_at:
            timestamps.append(last_survey.submitted_at)
        if last_usage:
            timestamps.append(last_usage.created_at)
        
        return max(timestamps) if timestamps else None

    # ==================== RESPONSE CONVERTERS ====================
    
    def _participant_to_response(self, participant: BetaTestingParticipant) -> BetaTestingParticipantResponse:
        """Convert participant model to response"""
        return BetaTestingParticipantResponse(
            id=participant.id,
            teacher_id=participant.teacher_id,
            beta_program_id=participant.beta_program_id,
            enrollment_date=participant.enrollment_date,
            status=participant.status,
            testing_phase=participant.testing_phase,
            assigned_features=participant.assigned_features,
            testing_goals=participant.testing_goals,
            contact_preferences=participant.contact_preferences,
            consent_given=participant.consent_given,
            consent_date=participant.consent_date,
            withdrawal_date=participant.withdrawal_date,
            completion_date=participant.completion_date,
            created_at=participant.created_at,
            updated_at=participant.updated_at
        )

    def _program_to_response(self, program: BetaTestingProgram) -> BetaTestingProgramResponse:
        """Convert program model to response"""
        return BetaTestingProgramResponse(
            id=program.id,
            program_name=program.program_name,
            program_description=program.program_description,
            program_type=program.program_type,
            target_audience=program.target_audience,
            max_participants=program.max_participants,
            current_participants=program.current_participants,
            start_date=program.start_date,
            end_date=program.end_date,
            is_active=program.is_active,
            success_criteria=program.success_criteria,
            metrics_to_track=program.metrics_to_track,
            created_at=program.created_at,
            updated_at=program.updated_at
        )

    def _feedback_to_response(self, feedback: BetaTestingFeedback) -> BetaTestingFeedbackResponse:
        """Convert feedback model to response"""
        return BetaTestingFeedbackResponse(
            id=feedback.id,
            participant_id=feedback.participant_id,
            feedback_type=feedback.feedback_type,
            feature_name=feedback.feature_name,
            feedback_title=feedback.feedback_title,
            feedback_description=feedback.feedback_description,
            severity_level=feedback.severity_level,
            priority_level=feedback.priority_level,
            user_impact=feedback.user_impact,
            reproduction_steps=feedback.reproduction_steps,
            expected_behavior=feedback.expected_behavior,
            actual_behavior=feedback.actual_behavior,
            browser_info=feedback.browser_info,
            device_info=feedback.device_info,
            screen_resolution=feedback.screen_resolution,
            operating_system=feedback.operating_system,
            additional_context=feedback.additional_context,
            is_resolved=feedback.is_resolved,
            resolution_notes=feedback.resolution_notes,
            resolved_at=feedback.resolved_at,
            resolved_by=feedback.resolved_by,
            created_at=feedback.created_at,
            updated_at=feedback.updated_at
        )

    def _survey_to_response(self, survey: BetaTestingSurvey) -> BetaTestingSurveyResponse:
        """Convert survey model to response"""
        return BetaTestingSurveyResponse(
            id=survey.id,
            program_id=survey.program_id,
            survey_name=survey.survey_name,
            survey_description=survey.survey_description,
            survey_type=survey.survey_type,
            survey_questions=survey.survey_questions,
            is_active=survey.is_active,
            start_date=survey.start_date,
            end_date=survey.end_date,
            created_at=survey.created_at,
            updated_at=survey.updated_at
        )

    def _survey_response_to_response(self, response: BetaTestingSurveyResponse) -> BetaTestingSurveyResponseResponse:
        """Convert survey response model to response"""
        return BetaTestingSurveyResponseResponse(
            id=response.id,
            participant_id=response.participant_id,
            survey_id=response.survey_id,
            response_data=response.response_data,
            completion_percentage=response.completion_percentage,
            time_spent_minutes=response.time_spent_minutes,
            is_completed=response.is_completed,
            submitted_at=response.submitted_at,
            created_at=response.created_at
        )

    def _usage_analytics_to_response(self, analytics: BetaTestingUsageAnalytics) -> BetaTestingUsageAnalyticsResponse:
        """Convert usage analytics model to response"""
        return BetaTestingUsageAnalyticsResponse(
            id=analytics.id,
            participant_id=analytics.participant_id,
            feature_name=analytics.feature_name,
            usage_date=analytics.usage_date,
            session_count=analytics.session_count,
            total_time_minutes=analytics.total_time_minutes,
            feature_interactions=analytics.feature_interactions,
            error_count=analytics.error_count,
            success_rate=analytics.success_rate,
            user_satisfaction_score=analytics.user_satisfaction_score,
            performance_metrics=analytics.performance_metrics,
            created_at=analytics.created_at
        )

    def _feature_flag_to_response(self, flag: BetaTestingFeatureFlag) -> BetaTestingFeatureFlagResponse:
        """Convert feature flag model to response"""
        return BetaTestingFeatureFlagResponse(
            id=flag.id,
            feature_name=flag.feature_name,
            feature_description=flag.feature_description,
            is_enabled=flag.is_enabled,
            rollout_percentage=flag.rollout_percentage,
            target_audience=flag.target_audience,
            enabled_for_participants=flag.enabled_for_participants,
            configuration=flag.configuration,
            created_at=flag.created_at,
            updated_at=flag.updated_at
        )

    def _notification_to_response(self, notification: BetaTestingNotification) -> BetaTestingNotificationResponse:
        """Convert notification model to response"""
        return BetaTestingNotificationResponse(
            id=notification.id,
            participant_id=notification.participant_id,
            notification_type=notification.notification_type,
            title=notification.title,
            message=notification.message,
            is_read=notification.is_read,
            action_url=notification.action_url,
            action_label=notification.action_label,
            priority_level=notification.priority_level,
            expires_at=notification.expires_at,
            created_at=notification.created_at,
            read_at=notification.read_at
        )
