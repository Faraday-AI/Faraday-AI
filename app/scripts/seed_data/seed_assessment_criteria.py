"""Seed assessment criteria data."""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.physical_education.skill_assessment.skill_assessment_models import AssessmentCriteria
from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.assessment import AssessmentCriteria as NewAssessmentCriteria
from app.models.physical_education.pe_enums.pe_types import (
    AssessmentType,
    AssessmentLevel,
    AssessmentStatus,
    AssessmentTrigger
)
from app.models.core.core_models import (
    CriteriaType,
    ChangeType
)
from app.models.physical_education.pe_enums.pe_types import SkillLevel

async def seed_assessment_criteria(session: AsyncSession) -> None:
    """Seed assessment criteria data."""
    print("Seeding assessment criteria...")

    criteria_data = [
        {
            "name": "Movement Form",
            "description": "Assessment of proper technique and form during movement execution",
            "criteria_type": "technical",
            "rubric": {
                "excellent": {
                    "description": "Perfect form throughout movement",
                    "score_range": [90, 100]
                },
                "good": {
                    "description": "Minor form deviations",
                    "score_range": [75, 89]
                },
                "satisfactory": {
                    "description": "Some form issues but maintains core technique",
                    "score_range": [60, 74]
                },
                "needs_improvement": {
                    "description": "Major form issues",
                    "score_range": [0, 59]
                }
            },
            "weight": 0.4,
            "min_score": 0,
            "max_score": 100
        },
        {
            "name": "Movement Control",
            "description": "Assessment of movement control and stability",
            "criteria_type": "technical",
            "rubric": {
                "excellent": {
                    "description": "Complete control throughout movement",
                    "score_range": [90, 100]
                },
                "good": {
                    "description": "Mostly controlled with minor instability",
                    "score_range": [75, 89]
                },
                "satisfactory": {
                    "description": "Some control issues but maintains safety",
                    "score_range": [60, 74]
                },
                "needs_improvement": {
                    "description": "Significant control issues",
                    "score_range": [0, 59]
                }
            },
            "weight": 0.3,
            "min_score": 0,
            "max_score": 100
        },
        {
            "name": "Performance Consistency",
            "description": "Assessment of consistent performance across repetitions",
            "criteria_type": "performance",
            "rubric": {
                "excellent": {
                    "description": "Highly consistent performance",
                    "score_range": [90, 100]
                },
                "good": {
                    "description": "Generally consistent with minor variations",
                    "score_range": [75, 89]
                },
                "satisfactory": {
                    "description": "Some inconsistency but acceptable",
                    "score_range": [60, 74]
                },
                "needs_improvement": {
                    "description": "Highly inconsistent performance",
                    "score_range": [0, 59]
                }
            },
            "weight": 0.3,
            "min_score": 0,
            "max_score": 100
        },
        {
            "name": "Safety Awareness",
            "description": "Assessment of safety awareness and practice",
            "criteria_type": "safety",
            "rubric": {
                "excellent": {
                    "description": "Excellent safety awareness and practice",
                    "score_range": [90, 100]
                },
                "good": {
                    "description": "Good safety awareness with minor lapses",
                    "score_range": [75, 89]
                },
                "satisfactory": {
                    "description": "Adequate safety awareness",
                    "score_range": [60, 74]
                },
                "needs_improvement": {
                    "description": "Poor safety awareness",
                    "score_range": [0, 59]
                }
            },
            "weight": 0.2,
            "min_score": 0,
            "max_score": 100
        },
        {
            "name": "Progress Rate",
            "description": "Assessment of improvement rate over time",
            "criteria_type": "progress",
            "rubric": {
                "excellent": {
                    "description": "Rapid and consistent improvement",
                    "score_range": [90, 100]
                },
                "good": {
                    "description": "Steady improvement",
                    "score_range": [75, 89]
                },
                "satisfactory": {
                    "description": "Moderate improvement",
                    "score_range": [60, 74]
                },
                "needs_improvement": {
                    "description": "Little to no improvement",
                    "score_range": [0, 59]
                }
            },
            "weight": 0.2,
            "min_score": 0,
            "max_score": 100
        }
    ]

    for data in criteria_data:
        criteria = NewAssessmentCriteria(**data)
        session.add(criteria)

    await session.flush()
    print("Assessment criteria seeded successfully!") 