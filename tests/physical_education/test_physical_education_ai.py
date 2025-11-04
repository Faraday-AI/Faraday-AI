import pytest
from datetime import datetime
from app.services.ai.ai_analytics import PhysicalEducationAI
from app.services.physical_education.pe_service import PEService
import json
import numpy as np
from typing import Dict, List, Any

@pytest.fixture
def pe_ai():
    """Create PhysicalEducationAI instance for testing."""
    return PhysicalEducationAI()

@pytest.fixture
def pe_service():
    """Create PEService instance for testing."""
    return PEService(service_type="physical_education")

@pytest.fixture
def sample_student_data():
    """Create sample student data for testing."""
    return {
        "student_id": "12345",
        "grade": 9,
        "fitness_level": "intermediate",
        "medical_conditions": [],
        "previous_injuries": [],
        "current_goals": ["improve cardiovascular endurance", "develop basketball skills"],
        "assessment_history": [
            {
                "date": "2024-03-01",
                "type": "fitness",
                "score": 0.75
            },
            {
                "date": "2024-03-15",
                "type": "skill",
                "score": 0.8
            }
        ]
    }

@pytest.fixture
def sample_class_data():
    """Create sample class data for testing."""
    return {
        "class_id": "PE101",
        "grade_level": "9th Grade",
        "class_size": 25,
        "available_equipment": ["basketballs", "cones", "whistles", "jump ropes"],
        "facility": {
            "type": "gymnasium",
            "dimensions": {"length": 100, "width": 50},
            "features": ["basketball_hoops", "volleyball_nets"]
        },
        "schedule": {
            "days": ["Monday", "Wednesday", "Friday"],
            "duration": "45 minutes"
        }
    }

@pytest.fixture
def sample_movement_data():
    """Create detailed sample movement data for testing."""
    return {
        "joint_positions": {
            "shoulder": np.array([[0.1, 0.2, 0.3], [0.2, 0.3, 0.4], [0.3, 0.4, 0.5]]),
            "elbow": np.array([[0.4, 0.5, 0.6], [0.5, 0.6, 0.7], [0.6, 0.7, 0.8]]),
            "wrist": np.array([[0.7, 0.8, 0.9], [0.8, 0.9, 1.0], [0.9, 1.0, 1.1]])
        },
        "timestamps": np.array([0.0, 0.1, 0.2]),
        "force_data": {
            "ground_reaction": np.array([[0.0, 0.0, 100.0], [0.0, 0.0, 150.0], [0.0, 0.0, 200.0]]),
            "joint_torques": {
                "shoulder": np.array([10.0, 15.0, 20.0]),
                "elbow": np.array([5.0, 7.5, 10.0])
            }
        },
        "metadata": {
            "activity": "Basketball Shot",
            "skill_level": "intermediate",
            "frame_rate": 30,
            "sensor_accuracy": 0.95
        }
    }

@pytest.fixture
def sample_biomechanical_data():
    """Create detailed biomechanical data for testing."""
    return {
        "kinematics": {
            "joint_angles": {
                "shoulder_flexion": np.array([90, 95, 100]),
                "elbow_flexion": np.array([45, 50, 55]),
                "wrist_extension": np.array([0, 5, 10])
            },
            "segment_velocities": {
                "upper_arm": np.array([1.0, 1.2, 1.4]),
                "forearm": np.array([1.5, 1.7, 1.9])
            }
        },
        "kinetics": {
            "joint_moments": {
                "shoulder": np.array([20.0, 25.0, 30.0]),
                "elbow": np.array([10.0, 12.5, 15.0])
            },
            "power": {
                "shoulder": np.array([50.0, 60.0, 70.0]),
                "elbow": np.array([25.0, 30.0, 35.0])
            }
        },
        "center_of_mass": {
            "position": np.array([[0.0, 0.0, 1.0], [0.1, 0.1, 1.1], [0.2, 0.2, 1.2]]),
            "velocity": np.array([[0.0, 0.0, 0.1], [0.1, 0.1, 0.2], [0.2, 0.2, 0.3]])
        }
    }

@pytest.mark.asyncio
async def test_generate_lesson_plan(pe_ai):
    """Test lesson plan generation."""
    result = await pe_ai.generate_lesson_plan(
        activity="Basketball Fundamentals",
        grade_level="9th Grade",
        duration="45 minutes"
    )
    
    assert "activity" in result
    assert "grade_level" in result
    assert "duration" in result
    assert result["activity"] == "Basketball Fundamentals"
    assert result["grade_level"] == "9th Grade"
    assert result["duration"] == "45 minutes"
    assert "objectives" in result
    assert "materials" in result
    assert "warm_up" in result
    assert "main_activity" in result
    assert "cool_down" in result
    assert "assessment" in result
    assert "modifications" in result
    assert "safety_notes" in result

@pytest.mark.asyncio
async def test_create_movement_instruction(pe_ai):
    """Test movement instruction creation."""
    result = await pe_ai.create_movement_instruction(
        activity="Basketball Shooting",
        skill_level="intermediate"
    )
    
    assert "instructions" in result
    assert "timestamp" in result
    assert "metadata" in result
    assert result["metadata"]["activity"] == "Basketball Shooting"
    assert result["metadata"]["skill_level"] == "intermediate"

@pytest.mark.asyncio
async def test_design_activity(pe_ai):
    """Test PE activity design."""
    equipment = ["basketballs", "cones", "whistles"]
    result = await pe_ai.design_activity(
        focus_area="Ball Handling",
        grade_level="9th Grade",
        equipment=equipment
    )
    
    assert "activity_design" in result
    assert "timestamp" in result
    assert "metadata" in result
    assert result["metadata"]["focus_area"] == "Ball Handling"
    assert result["metadata"]["grade_level"] == "9th Grade"
    assert result["metadata"]["equipment"] == equipment

@pytest.mark.asyncio
async def test_create_fitness_assessment(pe_ai):
    """Test fitness assessment plan creation."""
    focus_areas = ["cardiovascular endurance", "muscular strength"]
    result = await pe_ai.create_fitness_assessment(
        grade_level="9th Grade",
        focus_areas=focus_areas
    )
    
    assert "assessment_plan" in result
    assert "timestamp" in result
    assert "metadata" in result
    assert result["metadata"]["grade_level"] == "9th Grade"
    assert result["metadata"]["focus_areas"] == focus_areas

@pytest.mark.asyncio
async def test_optimize_classroom(pe_ai):
    """Test classroom management optimization."""
    space = {"type": "gymnasium", "dimensions": {"length": 100, "width": 50}}
    equipment = ["basketballs", "cones", "whistles"]
    
    result = await pe_ai.optimize_classroom(
        size=25,
        space=space,
        equipment=equipment
    )
    
    assert "optimization_plan" in result
    assert "group_suggestions" in result
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_assess_skills(pe_ai):
    """Test skill assessment."""
    performance = {
        "attempts": 10,
        "successful": 7,
        "form_rating": 0.8,
        "speed": "moderate"
    }
    previous = [
        {
            "date": "2024-03-01",
            "score": 0.7
        },
        {
            "date": "2024-03-15",
            "score": 0.75
        }
    ]
    
    result = await pe_ai.assess_skills(
        activity="Basketball Free Throws",
        performance=performance,
        previous=previous
    )
    
    assert "assessment" in result
    assert "base_score" in result["assessment"]
    assert "detailed_analysis" in result["assessment"]
    assert "progress_tracking" in result["assessment"]
    assert "goal_recommendations" in result["assessment"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_integrate_curriculum(pe_ai):
    """Test curriculum integration."""
    standards = [
        "2.5.12.A.1",
        "2.5.12.A.2",
        "2.5.12.B.1"
    ]
    
    result = await pe_ai.integrate_curriculum(
        subject="Mathematics",
        grade_level="9th Grade",
        standards=standards
    )
    
    assert "integration_plan" in result
    assert "resource_recommendations" in result
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_safety(pe_ai):
    """Test safety analysis."""
    activity = {
        "type": "Basketball",
        "equipment": ["basketballs", "cones"],
        "space_requirements": {"min_area": 1000, "min_height": 20},
        "participants": 25,
        "skill_level": "intermediate"
    }
    
    result = await pe_ai.analyze_safety(activity)
    
    assert "safety_assessment" in result
    assert "risk_factors" in result["safety_assessment"]
    assert "mitigation_strategies" in result["safety_assessment"]
    assert "equipment_requirements" in result["safety_assessment"]
    assert "supervision_requirements" in result["safety_assessment"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_error_handling(pe_ai):
    """Test error handling."""
    with pytest.raises(Exception):
        await pe_ai.generate_lesson_plan(None, None, None)
    
    with pytest.raises(Exception):
        await pe_ai.create_movement_instruction(None, None)
    
    with pytest.raises(Exception):
        await pe_ai.design_activity(None, None, None)

@pytest.mark.asyncio
async def test_rate_limiting(pe_ai):
    """Test rate limiting functionality."""
    # Test rapid consecutive calls
    for _ in range(5):
        result = await pe_ai.generate_lesson_plan(
            activity="Basketball Fundamentals",
            grade_level="9th Grade",
            duration="45 minutes"
        )
        assert result is not None
    
    # Test with delay
    import asyncio
    await asyncio.sleep(1)
    
    result = await pe_ai.generate_lesson_plan(
        activity="Basketball Fundamentals",
        grade_level="9th Grade",
        duration="45 minutes"
    )
    assert result is not None

@pytest.mark.asyncio
async def test_create_personalized_workout(pe_ai, sample_student_data):
    """Test personalized workout creation."""
    result = await pe_ai.create_personalized_workout(
        student_data=sample_student_data,
        focus_areas=["cardiovascular", "strength"],
        duration=30
    )
    
    assert "workout_plan" in result
    assert "exercises" in result["workout_plan"]
    assert "intensity_level" in result["workout_plan"]
    assert "duration" in result["workout_plan"]
    assert "rest_periods" in result["workout_plan"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_generate_progress_report(pe_ai, sample_student_data):
    """Test progress report generation."""
    result = await pe_ai.generate_progress_report(
        student_data=sample_student_data,
        time_period="monthly"
    )
    
    assert "progress_report" in result
    assert "fitness_metrics" in result["progress_report"]
    assert "skill_development" in result["progress_report"]
    assert "goal_tracking" in result["progress_report"]
    assert "recommendations" in result["progress_report"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_create_adaptive_lesson(pe_ai, sample_class_data):
    """Test adaptive lesson creation."""
    result = await pe_ai.create_adaptive_lesson(
        class_data=sample_class_data,
        topic="Basketball Fundamentals",
        duration="45 minutes"
    )
    
    assert "adaptive_lesson" in result
    assert "core_activities" in result["adaptive_lesson"]
    assert "modifications" in result["adaptive_lesson"]
    assert "assessment_strategies" in result["adaptive_lesson"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_movement_patterns(pe_ai):
    """Test movement pattern analysis."""
    movement_data = {
        "joint_positions": {
            "shoulder": np.array([[0.1, 0.2, 0.3], [0.2, 0.3, 0.4]]),
            "elbow": np.array([[0.4, 0.5, 0.6], [0.5, 0.6, 0.7]])
        },
        "timestamps": np.array([0.0, 0.1]),
        "metadata": {
            "activity": "Basketball Shot",
            "skill_level": "intermediate"
        }
    }
    
    result = await pe_ai.analyze_movement_patterns(movement_data)
    
    assert "pattern_analysis" in result
    assert "joint_trajectories" in result["pattern_analysis"]
    assert "movement_phases" in result["pattern_analysis"]
    assert "efficiency_metrics" in result["pattern_analysis"]
    assert "recommendations" in result["pattern_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_create_injury_prevention_plan(pe_ai, sample_student_data):
    """Test injury prevention plan creation."""
    result = await pe_ai.create_injury_prevention_plan(
        student_data=sample_student_data,
        activity_type="Basketball"
    )
    
    assert "prevention_plan" in result
    assert "risk_assessment" in result["prevention_plan"]
    assert "warmup_routine" in result["prevention_plan"]
    assert "strengthening_exercises" in result["prevention_plan"]
    assert "recovery_strategies" in result["prevention_plan"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_generate_skill_progression(pe_ai):
    """Test skill progression generation."""
    result = await pe_ai.generate_skill_progression(
        activity="Basketball",
        skill_level="beginner",
        target_level="intermediate"
    )
    
    assert "progression_plan" in result
    assert "skill_milestones" in result["progression_plan"]
    assert "practice_drills" in result["progression_plan"]
    assert "assessment_criteria" in result["progression_plan"]
    assert "timeline" in result["progression_plan"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_create_competition_preparation(pe_ai, sample_class_data):
    """Test competition preparation plan creation."""
    result = await pe_ai.create_competition_preparation(
        class_data=sample_class_data,
        competition_type="Basketball Tournament",
        preparation_time="4 weeks"
    )
    
    assert "preparation_plan" in result
    assert "training_schedule" in result["preparation_plan"]
    assert "skill_focus" in result["preparation_plan"]
    assert "team_strategies" in result["preparation_plan"]
    assert "recovery_plan" in result["preparation_plan"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_team_dynamics(pe_ai, sample_class_data):
    """Test team dynamics analysis."""
    result = await pe_ai.analyze_team_dynamics(
        class_data=sample_class_data,
        activity_type="Basketball"
    )
    
    assert "dynamics_analysis" in result
    assert "team_roles" in result["dynamics_analysis"]
    assert "communication_patterns" in result["dynamics_analysis"]
    assert "leadership_distribution" in result["dynamics_analysis"]
    assert "recommendations" in result["dynamics_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_create_cross_curricular_activity(pe_ai):
    """Test cross-curricular activity creation."""
    result = await pe_ai.create_cross_curricular_activity(
        subject="Mathematics",
        activity_type="Basketball",
        grade_level="9th Grade"
    )
    
    assert "activity_plan" in result
    assert "learning_objectives" in result["activity_plan"]
    assert "activity_description" in result["activity_plan"]
    assert "assessment_methods" in result["activity_plan"]
    assert "resource_requirements" in result["activity_plan"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_generate_professional_development(pe_ai):
    """Test professional development plan generation."""
    result = await pe_ai.generate_professional_development(
        focus_areas=["Basketball Coaching", "Sports Science"],
        experience_level="intermediate"
    )
    
    assert "development_plan" in result
    assert "learning_goals" in result["development_plan"]
    assert "training_modules" in result["development_plan"]
    assert "assessment_methods" in result["development_plan"]
    assert "timeline" in result["development_plan"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_create_emergency_response_plan(pe_ai, sample_class_data):
    """Test emergency response plan creation."""
    result = await pe_ai.create_emergency_response_plan(
        class_data=sample_class_data,
        activity_type="Basketball"
    )
    
    assert "response_plan" in result
    assert "emergency_procedures" in result["response_plan"]
    assert "first_aid_requirements" in result["response_plan"]
    assert "communication_protocol" in result["response_plan"]
    assert "evacuation_routes" in result["response_plan"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_equipment_needs(pe_ai, sample_class_data):
    """Test equipment needs analysis."""
    result = await pe_ai.analyze_equipment_needs(
        class_data=sample_class_data,
        activity_type="Basketball"
    )
    
    assert "equipment_analysis" in result
    assert "required_equipment" in result["equipment_analysis"]
    assert "quantity_requirements" in result["equipment_analysis"]
    assert "maintenance_schedule" in result["equipment_analysis"]
    assert "safety_checks" in result["equipment_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_create_seasonal_plan(pe_ai, sample_class_data):
    """Test seasonal plan creation."""
    result = await pe_ai.create_seasonal_plan(
        class_data=sample_class_data,
        season="Spring",
        duration="12 weeks"
    )
    
    assert "seasonal_plan" in result
    assert "curriculum_outline" in result["seasonal_plan"]
    assert "activity_schedule" in result["seasonal_plan"]
    assert "assessment_timeline" in result["seasonal_plan"]
    assert "resource_allocation" in result["seasonal_plan"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_movement_technique(pe_ai, sample_movement_data):
    """Test movement technique analysis."""
    result = await pe_ai.analyze_movement_technique(sample_movement_data)
    
    assert "technique_analysis" in result
    assert "form_assessment" in result["technique_analysis"]
    assert "efficiency_metrics" in result["technique_analysis"]
    assert "improvement_areas" in result["technique_analysis"]
    assert "recommendations" in result["technique_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_biomechanics(pe_ai, sample_biomechanical_data):
    """Test biomechanical analysis."""
    result = await pe_ai.analyze_biomechanics(sample_biomechanical_data)
    
    assert "biomechanical_analysis" in result
    assert "kinematic_analysis" in result["biomechanical_analysis"]
    assert "kinetic_analysis" in result["biomechanical_analysis"]
    assert "efficiency_metrics" in result["biomechanical_analysis"]
    assert "recommendations" in result["biomechanical_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_movement_efficiency(pe_ai, sample_movement_data, sample_biomechanical_data):
    """Test movement efficiency analysis."""
    result = await pe_ai.analyze_movement_efficiency(sample_movement_data, sample_biomechanical_data)
    
    assert "efficiency_analysis" in result
    assert "energy_expenditure" in result["efficiency_analysis"]
    assert "mechanical_efficiency" in result["efficiency_analysis"]
    assert "optimization_opportunities" in result["efficiency_analysis"]
    assert "recommendations" in result["efficiency_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_injury_risk(pe_ai, sample_movement_data, sample_biomechanical_data):
    """Test injury risk analysis."""
    result = await pe_ai.analyze_injury_risk(sample_movement_data, sample_biomechanical_data)
    
    assert "risk_analysis" in result
    assert "risk_factors" in result["risk_analysis"]
    assert "vulnerable_areas" in result["risk_analysis"]
    assert "prevention_strategies" in result["risk_analysis"]
    assert "recommendations" in result["risk_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_performance_metrics(pe_ai, sample_movement_data, sample_biomechanical_data):
    """Test performance metrics analysis."""
    result = await pe_ai.analyze_performance_metrics(sample_movement_data, sample_biomechanical_data)
    
    assert "performance_analysis" in result
    assert "power_metrics" in result["performance_analysis"]
    assert "speed_metrics" in result["performance_analysis"]
    assert "accuracy_metrics" in result["performance_analysis"]
    assert "consistency_metrics" in result["performance_analysis"]
    assert "recommendations" in result["performance_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_movement_adaptation(pe_ai, sample_movement_data):
    """Test movement adaptation analysis."""
    result = await pe_ai.analyze_movement_adaptation(sample_movement_data)
    
    assert "adaptation_analysis" in result
    assert "movement_variations" in result["adaptation_analysis"]
    assert "adaptation_patterns" in result["adaptation_analysis"]
    assert "effectiveness_metrics" in result["adaptation_analysis"]
    assert "recommendations" in result["adaptation_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_movement_learning(pe_ai, sample_movement_data):
    """Test movement learning analysis."""
    result = await pe_ai.analyze_movement_learning(sample_movement_data)
    
    assert "learning_analysis" in result
    assert "skill_acquisition" in result["learning_analysis"]
    assert "learning_rate" in result["learning_analysis"]
    assert "retention_metrics" in result["learning_analysis"]
    assert "recommendations" in result["learning_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_movement_fatigue(pe_ai, sample_movement_data):
    """Test movement fatigue analysis."""
    result = await pe_ai.analyze_movement_fatigue(sample_movement_data)
    
    assert "fatigue_analysis" in result
    assert "fatigue_indicators" in result["fatigue_analysis"]
    assert "performance_degradation" in result["fatigue_analysis"]
    assert "recovery_needs" in result["fatigue_analysis"]
    assert "recommendations" in result["fatigue_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_movement_symmetry(pe_ai, sample_movement_data):
    """Test movement symmetry analysis."""
    result = await pe_ai.analyze_movement_symmetry(sample_movement_data)
    
    assert "symmetry_analysis" in result
    assert "bilateral_comparison" in result["symmetry_analysis"]
    assert "asymmetry_metrics" in result["symmetry_analysis"]
    assert "compensation_patterns" in result["symmetry_analysis"]
    assert "recommendations" in result["symmetry_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_movement_consistency(pe_ai, sample_movement_data):
    """Test movement consistency analysis."""
    result = await pe_ai.analyze_movement_consistency(sample_movement_data)
    
    assert "consistency_analysis" in result
    assert "variability_metrics" in result["consistency_analysis"]
    assert "pattern_stability" in result["consistency_analysis"]
    assert "reliability_metrics" in result["consistency_analysis"]
    assert "recommendations" in result["consistency_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_movement_environment(pe_ai, sample_movement_data):
    """Test movement environment analysis."""
    result = await pe_ai.analyze_movement_environment(sample_movement_data)
    
    assert "environment_analysis" in result
    assert "spatial_requirements" in result["environment_analysis"]
    assert "environmental_factors" in result["environment_analysis"]
    assert "safety_considerations" in result["environment_analysis"]
    assert "recommendations" in result["environment_analysis"]
    assert "timestamp" in result

@pytest.mark.asyncio
async def test_analyze_movement_equipment(pe_ai, sample_movement_data):
    """Test movement equipment analysis."""
    result = await pe_ai.analyze_movement_equipment(sample_movement_data)
    
    assert "equipment_analysis" in result
    assert "equipment_requirements" in result["equipment_analysis"]
    assert "equipment_effectiveness" in result["equipment_analysis"]
    assert "safety_considerations" in result["equipment_analysis"]
    assert "recommendations" in result["equipment_analysis"]
    assert "timestamp" in result 