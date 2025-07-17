"""Seed skill assessment data."""
from datetime import datetime, timedelta
import random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill_assessment.assessment.assessment import (
    SkillAssessment, AssessmentResult, AssessmentHistory, SkillProgress, AssessmentCriteria
)
from app.models.student import Student
from app.models.activity import Activity

async def seed_skill_assessments(session: AsyncSession) -> None:
    """Seed skill assessment data."""
    print("Seeding skill assessments...")

    # Get students, activities, and criteria
    students = (await session.execute(select(Student))).scalars().all()
    activities = (await session.execute(select(Activity))).scalars().all()
    criteria = (await session.execute(select(AssessmentCriteria))).scalars().all()

    # Create assessments for each student-activity pair
    for student in students[:5]:  # Limit to first 5 students
        for activity in activities[:3]:  # Limit to first 3 activities
            # Create skill assessment
            assessment = SkillAssessment(
                student_id=student.id,
                activity_id=activity.id,
                assessor_notes="Initial skill assessment",
                assessment_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                overall_score=random.uniform(60, 95),
                status="completed",
                assessment_metadata={
                    "form": random.uniform(60, 95),
                    "technique": random.uniform(60, 95),
                    "consistency": random.uniform(60, 95)
                }
            )
            session.add(assessment)
            await session.flush()

            # Calculate overall score from criteria scores
            total_weighted_score = 0
            total_weight = 0

            # Create assessment results for each criteria
            for criterion in criteria:
                score = random.uniform(60, 95)
                result = AssessmentResult(
                    assessment_id=assessment.id,
                    criteria_id=criterion.id,
                    score=score,
                    notes=f"Assessment for {criterion.name}",
                    evidence={
                        "observations": ["Good form", "Consistent performance"],
                        "measurements": {
                            "attempts": random.randint(3, 8),
                            "successful": random.randint(2, 6)
                        }
                    }
                )
                session.add(result)
                total_weighted_score += score * criterion.weight
                total_weight += criterion.weight

            # Update overall score
            assessment.overall_score = total_weighted_score / total_weight if total_weight > 0 else 0

            # Create assessment history
            history = AssessmentHistory(
                assessment_id=assessment.id,
                change_type="created",
                previous_state={},
                new_state={
                    "status": "completed",
                    "overall_score": assessment.overall_score
                },
                reason="Initial assessment completion"
            )
            session.add(history)

            # Create skill progress
            progress = SkillProgress(
                student_id=student.id,
                activity_id=activity.id,
                skill_level="beginner" if assessment.overall_score < 70 else "intermediate" if assessment.overall_score < 85 else "advanced",
                progress_data={
                    "initial_score": assessment.overall_score,
                    "strengths": ["form", "effort"],
                    "areas_for_improvement": ["consistency", "speed"],
                    "milestones_achieved": ["basic_form", "safety_awareness"]
                },
                last_assessment_date=assessment.created_at,
                next_assessment_date=assessment.created_at + timedelta(days=30),
                goals={
                    "short_term": ["Improve form consistency", "Increase speed"],
                    "long_term": ["Master advanced techniques", "Achieve expert level"]
                }
            )
            session.add(progress)

    await session.flush()
    print("Skill assessments seeded successfully!") 