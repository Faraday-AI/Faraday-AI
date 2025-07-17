import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.main import app
from app.db.session import get_db
from app.services.physical_education.models.activity import (
    Activity,
    ActivityCategory,
    ActivityRecommendation,
    Student,
    Class,
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    StudentActivityPerformance
)
from app.api.v1.models.activity import ActivityType, DifficultyLevel
from app.models.physical_education.class_ import PhysicalEducationClass
from app.models.physical_education.student import Student
from app.services.physical_education.activity_recommendations import ActivityRecommendationService
from app.core.database import Base, engine
from app.models.shared_base import SharedBase

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def db():
    SharedBase.metadata.create_all(bind=engine)
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
        SharedBase.metadata.drop_all(bind=engine)

@pytest.fixture
def test_student(db: Session):
    student = Student(
        id=1,
        name="Test Student",
        grade_level=9,
        skill_level="intermediate",
        fitness_level="moderate"
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@pytest.fixture
def test_class(db: Session):
    pe_class = PhysicalEducationClass(
        id=1,
        name="Test Class",
        grade_level=9,
        class_type="physical_education",
        duration_minutes=45
    )
    db.add(pe_class)
    db.commit()
    db.refresh(pe_class)
    return pe_class

@pytest.fixture
def test_activities(db: Session):
    activities = []
    for i in range(1, 6):
        activity = Activity(
            id=i,
            name=f"Test Activity {i}",
            description=f"Test Description {i}",
            activity_type=ActivityType.STRENGTH if i % 2 == 0 else ActivityType.CARDIO,
            difficulty_level="intermediate",
            duration_minutes=30
        )
        db.add(activity)
        activities.append(activity)
    
    db.commit()
    for activity in activities:
        db.refresh(activity)
    return activities

@pytest.fixture
def test_categories(db: Session, test_activities):
    categories = []
    for i in range(1, 4):
        category = ActivityCategory(
            id=i,
            name=f"Test Category {i}",
            description=f"Test Category Description {i}"
        )
        db.add(category)
        categories.append(category)
    
    db.commit()
    for category in categories:
        db.refresh(category)
    
    # Associate activities with categories
    for i, activity in enumerate(test_activities):
        activity_category = ActivityCategory(
            activity_id=activity.id,
            category_id=categories[i % 3].id
        )
        db.add(activity_category)
    
    db.commit()
    return categories

@pytest.fixture
def test_recommendations(db: Session, test_student, test_class, test_activities):
    recommendations = []
    for i, activity in enumerate(test_activities):
        recommendation = ActivityRecommendation(
            id=i + 1,
            student_id=test_student.id,
            class_id=test_class.id,
            activity_id=activity.id,
            recommendation_score=0.9 - (i * 0.1),
            score_breakdown={
                "skill_match": 0.9,
                "fitness_match": 0.8,
                "preference_match": 0.85
            },
            created_at=datetime.now() - timedelta(days=i)
        )
        db.add(recommendation)
        recommendations.append(recommendation)
    
    db.commit()
    for recommendation in recommendations:
        db.refresh(recommendation)
    return recommendations

def test_get_activity_recommendations(client, test_student, test_class):
    # Test with valid request
    response = client.post(
        "/api/v1/physical-education/recommendations",
        json={
            "student_id": test_student.id,
            "class_id": test_class.id,
            "preferences": {
                "difficulty_level": "intermediate",
                "activity_types": ["strength", "cardio"],
                "duration_minutes": 30
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all("recommendation_score" in item for item in data)

def test_get_recommendation_history(client, test_student, test_recommendations):
    # Test with valid student ID
    response = client.get(f"/api/v1/physical-education/recommendations/history/{test_student.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(item["student_id"] == test_student.id for item in data)

def test_get_category_recommendations(client, test_student, test_class, test_categories):
    # Test with valid category ID
    response = client.get(
        f"/api/v1/physical-education/recommendations/category/{test_student.id}/{test_class.id}/{test_categories[0].id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all("activity_id" in item for item in data)

def test_get_balanced_recommendations(client, test_student, test_class):
    # Test with valid student and class IDs
    response = client.get(
        f"/api/v1/physical-education/recommendations/balanced/{test_student.id}/{test_class.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all("recommendation_score" in item for item in data)

def test_clear_recommendations(client, test_student, test_recommendations):
    # Test clearing recommendations
    response = client.delete(f"/api/v1/physical-education/recommendations/{test_student.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Recommendations cleared successfully"

def test_get_activity_recommendations_invalid_student(client):
    # Test with invalid student ID
    response = client.post(
        "/api/v1/physical-education/recommendations",
        json={
            "student_id": 999,
            "class_id": 1,
            "preferences": {
                "difficulty_level": "intermediate",
                "activity_types": ["strength", "cardio"],
                "duration_minutes": 30
            }
        }
    )
    assert response.status_code == 404

def test_get_category_recommendations_invalid_category(client, test_student, test_class):
    # Test with invalid category ID
    response = client.get(
        f"/api/v1/physical-education/recommendations/category/{test_student.id}/{test_class.id}/999"
    )
    assert response.status_code == 404

def test_get_balanced_recommendations_invalid_class(client, test_student):
    # Test with invalid class ID
    response = client.get(
        f"/api/v1/physical-education/recommendations/balanced/{test_student.id}/999"
    )
    assert response.status_code == 404

def test_get_activity_recommendations_with_filters(client, test_student, test_class, test_activities):
    # Test with min_score filter
    response = client.post(
        "/api/v1/physical-education/recommendations",
        params={"min_score": 0.8},
        json={
            "student_id": test_student.id,
            "class_id": test_class.id,
            "preferences": {
                "difficulty_level": "intermediate",
                "activity_types": ["strength", "cardio"],
                "duration_minutes": 30
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(item["recommendation_score"] >= 0.8 for item in data)

    # Test with max_duration filter
    response = client.post(
        "/api/v1/physical-education/recommendations",
        params={"max_duration": 20},
        json={
            "student_id": test_student.id,
            "class_id": test_class.id,
            "preferences": {
                "difficulty_level": "intermediate",
                "activity_types": ["strength", "cardio"],
                "duration_minutes": 30
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(item["duration_minutes"] <= 20 for item in data)

    # Test with exclude_recent filter
    response = client.post(
        "/api/v1/physical-education/recommendations",
        params={"exclude_recent": True},
        json={
            "student_id": test_student.id,
            "class_id": test_class.id,
            "preferences": {
                "difficulty_level": "intermediate",
                "activity_types": ["strength", "cardio"],
                "duration_minutes": 30
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_get_recommendation_history_with_filters(client, test_student, test_recommendations):
    # Test with date range filter
    start_date = (datetime.now() - timedelta(days=3)).isoformat()
    end_date = datetime.now().isoformat()
    response = client.get(
        f"/api/v1/physical-education/recommendations/history/{test_student.id}",
        params={
            "start_date": start_date,
            "end_date": end_date
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

    # Test with min_score filter
    response = client.get(
        f"/api/v1/physical-education/recommendations/history/{test_student.id}",
        params={"min_score": 0.8}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(item["recommendation_score"] >= 0.8 for item in data)

    # Test with activity_type filter
    response = client.get(
        f"/api/v1/physical-education/recommendations/history/{test_student.id}",
        params={"activity_type": ActivityType.STRENGTH}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_get_category_recommendations_with_filters(client, test_student, test_class, test_categories):
    # Test with difficulty_level filter
    response = client.get(
        f"/api/v1/physical-education/recommendations/category/{test_student.id}/{test_class.id}/{test_categories[0].id}",
        params={"difficulty_level": DifficultyLevel.INTERMEDIATE}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

    # Test with min_score filter
    response = client.get(
        f"/api/v1/physical-education/recommendations/category/{test_student.id}/{test_class.id}/{test_categories[0].id}",
        params={"min_score": 0.8}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(item["recommendation_score"] >= 0.8 for item in data)

    # Test with max_duration filter
    response = client.get(
        f"/api/v1/physical-education/recommendations/category/{test_student.id}/{test_class.id}/{test_categories[0].id}",
        params={"max_duration": 20}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_get_balanced_recommendations_with_filters(client, test_student, test_class):
    # Test with activity_types filter
    response = client.get(
        f"/api/v1/physical-education/recommendations/balanced/{test_student.id}/{test_class.id}",
        params={"activity_types": [ActivityType.STRENGTH, ActivityType.CARDIO]}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

    # Test with difficulty_levels filter
    response = client.get(
        f"/api/v1/physical-education/recommendations/balanced/{test_student.id}/{test_class.id}",
        params={"difficulty_levels": [DifficultyLevel.INTERMEDIATE]}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

    # Test with min_score filter
    response = client.get(
        f"/api/v1/physical-education/recommendations/balanced/{test_student.id}/{test_class.id}",
        params={"min_score": 0.8}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(item["recommendation_score"] >= 0.8 for item in data)

def test_clear_recommendations_with_date_filter(client, test_student, test_recommendations):
    # Test clearing recommendations before a specific date
    before_date = (datetime.now() - timedelta(days=2)).isoformat()
    response = client.delete(
        f"/api/v1/physical-education/recommendations/{test_student.id}",
        params={"before_date": before_date}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Recommendations cleared successfully"

def test_get_recommendations_for_class(db, sample_class):
    service = ActivityRecommendationService(db)
    recommendations = service.get_recommendations_for_class(sample_class.id)
    assert isinstance(recommendations, list)

def test_get_recommendations_for_student(db, sample_student):
    service = ActivityRecommendationService(db)
    recommendations = service.get_recommendations_for_student(sample_student.id)
    assert isinstance(recommendations, list)

def test_update_recommendations(db, sample_class):
    service = ActivityRecommendationService(db)
    success = service.update_recommendations(sample_class.id)
    assert success is True 