from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, ARRAY, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.models.shared_base import SharedBase as Base

class BetaTestingParticipant(Base):
    __tablename__ = "beta_testing_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teacher_registrations.id"), nullable=False)
    beta_program_id = Column(UUID(as_uuid=True), ForeignKey("beta_testing_programs.id"), nullable=False)
    email = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    organization = Column(String(255))
    role = Column(String(100))
    experience_level = Column(String(50))
    interests = Column(ARRAY(String), default=list)
    notes = Column(Text)
    status = Column(String(50), default="active")  # active, inactive, suspended
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    teacher = relationship("app.models.teacher_registration.TeacherRegistration", back_populates="beta_participants")
    beta_program = relationship("app.models.beta_testing.BetaTestingProgram", back_populates="participants")
    feedback = relationship("app.models.beta_testing.BetaTestingFeedback", back_populates="participant")
    survey_responses = relationship("app.models.beta_testing.BetaTestingSurveyResponse", back_populates="participant")
    usage_analytics = relationship("app.models.beta_testing.BetaTestingUsageAnalytics", back_populates="participant")

class BetaTestingProgram(Base):
    __tablename__ = "beta_testing_programs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(50), nullable=False)
    status = Column(String(50), default="draft")  # draft, active, completed, cancelled
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    max_participants = Column(Integer)
    requirements = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    participants = relationship("app.models.beta_testing.BetaTestingParticipant", back_populates="beta_program")
    feedback = relationship("app.models.beta_testing.BetaTestingFeedback", back_populates="beta_program")
    surveys = relationship("app.models.beta_testing.BetaTestingSurvey", back_populates="beta_program")
    usage_analytics = relationship("app.models.beta_testing.BetaTestingUsageAnalytics", back_populates="beta_program")

class BetaTestingFeedback(Base):
    __tablename__ = "beta_testing_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("beta_testing_participants.id"), nullable=False)
    beta_program_id = Column(UUID(as_uuid=True), ForeignKey("beta_testing_programs.id"), nullable=False)
    feedback_type = Column(String(50), nullable=False)  # bug_report, feature_request, general, usability
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(50), default="open")  # open, in_progress, resolved, closed
    tags = Column(ARRAY(String), default=list)
    attachments = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    participant = relationship("app.models.beta_testing.BetaTestingParticipant", back_populates="feedback")
    beta_program = relationship("app.models.beta_testing.BetaTestingProgram", back_populates="feedback")

class BetaTestingSurvey(Base):
    __tablename__ = "beta_testing_surveys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beta_program_id = Column(UUID(as_uuid=True), ForeignKey("beta_testing_programs.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    questions = Column(JSON, nullable=False)
    status = Column(String(50), default="draft")  # draft, active, closed
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    beta_program = relationship("app.models.beta_testing.BetaTestingProgram", back_populates="surveys")
    responses = relationship("app.models.beta_testing.BetaTestingSurveyResponse", back_populates="survey")

class BetaTestingSurveyResponse(Base):
    __tablename__ = "beta_testing_survey_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("beta_testing_surveys.id"), nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("beta_testing_participants.id"), nullable=False)
    responses = Column(JSON, nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    survey = relationship("app.models.beta_testing.BetaTestingSurvey", back_populates="responses")
    participant = relationship("app.models.beta_testing.BetaTestingParticipant", back_populates="survey_responses")

class BetaTestingUsageAnalytics(Base):
    __tablename__ = "beta_testing_usage_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("beta_testing_participants.id"), nullable=False)
    beta_program_id = Column(UUID(as_uuid=True), ForeignKey("beta_testing_programs.id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON)
    session_id = Column(String(255))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    participant = relationship("app.models.beta_testing.BetaTestingParticipant", back_populates="usage_analytics")
    beta_program = relationship("app.models.beta_testing.BetaTestingProgram", back_populates="usage_analytics")

class BetaTestingFeatureFlag(Base):
    __tablename__ = "beta_testing_feature_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    is_enabled = Column(Boolean, default=False)
    target_percentage = Column(Integer, default=0)  # 0-100
    conditions = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class BetaTestingNotification(Base):
    __tablename__ = "beta_testing_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("beta_testing_participants.id"), nullable=False)
    type = Column(String(50), nullable=False)  # email, in_app, sms
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    participant = relationship("app.models.beta_testing.BetaTestingParticipant")

class BetaTestingReport(Base):
    __tablename__ = "beta_testing_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beta_program_id = Column(UUID(as_uuid=True), ForeignKey("beta_testing_programs.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # summary, detailed, analytics
    title = Column(String(255), nullable=False)
    content = Column(JSON, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    beta_program = relationship("app.models.beta_testing.BetaTestingProgram")
