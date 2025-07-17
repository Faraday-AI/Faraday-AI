"""
Tests for the resource optimization service.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import numpy as np

from ..services.resource_optimization_service import ResourceOptimizationService
from ..models import (
    GPTDefinition,
    GPTSubscription,
    GPTPerformance,
    GPTUsageHistory,
    GPTCategory,
    GPTType
)

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_analytics_service():
    with patch("app.dashboard.services.analytics_service.AnalyticsService") as mock:
        yield mock

@pytest.fixture
def optimization_service(mock_db):
    return ResourceOptimizationService(mock_db)

@pytest.fixture
def sample_usage_prediction():
    return {
        "status": "success",
        "predictions": {
            "predicted_peak_usage": 0.75,
            "growth_trend": 0.1,
            "peak_hours": [9, 14, 16]
        },
        "confidence_score": 0.8
    }

@pytest.fixture
def sample_performance_trends():
    return {
        "status": "success",
        "trends": {
            "response_time": {
                "current_value": 0.5,
                "trend": "improving"
            },
            "accuracy": {
                "current_value": 0.85,
                "trend": "stable"
            }
        },
        "performance_score": 0.8
    }

async def test_optimize_resources(
    optimization_service,
    mock_analytics_service,
    sample_usage_prediction,
    sample_performance_trends
):
    """Test resource optimization."""
    # Mock analytics service responses
    mock_analytics_service.return_value.predict_resource_usage.return_value = (
        sample_usage_prediction
    )
    mock_analytics_service.return_value.get_performance_trends.return_value = (
        sample_performance_trends
    )

    # Test balanced optimization
    result = await optimization_service.optimize_resources(
        gpt_id="gpt-1",
        optimization_target="balanced"
    )
    
    assert result["status"] == "success"
    assert "optimization_plan" in result
    assert "scaling_recommendations" in result
    assert "estimated_improvements" in result
    
    # Verify optimization plan
    plan = result["optimization_plan"]
    assert plan["buffer_strategy"] == "moderate"
    assert 0.8 <= plan["recommended_allocation"] <= 1.2

    # Test performance-focused optimization
    result = await optimization_service.optimize_resources(
        gpt_id="gpt-1",
        optimization_target="performance"
    )
    
    assert result["optimization_plan"]["buffer_strategy"] == "aggressive"
    
    # Test efficiency-focused optimization
    result = await optimization_service.optimize_resources(
        gpt_id="gpt-1",
        optimization_target="efficiency"
    )
    
    assert result["optimization_plan"]["buffer_strategy"] == "minimal"

async def test_get_resource_allocation_plan(
    optimization_service,
    mock_db,
    mock_analytics_service,
    sample_usage_prediction
):
    """Test resource allocation planning."""
    # Mock database queries
    mock_db.query.return_value.filter.return_value.all.return_value = [
        GPTDefinition(
            id="gpt-1",
            name="Math Teacher",
            category=GPTCategory.TEACHER,
            type=GPTType.MATH_TEACHER
        ),
        GPTDefinition(
            id="gpt-2",
            name="Science Teacher",
            category=GPTCategory.TEACHER,
            type=GPTType.SCIENCE_TEACHER
        )
    ]
    
    # Mock analytics service
    mock_analytics_service.return_value.predict_resource_usage.return_value = (
        sample_usage_prediction
    )

    # Test allocation plan generation
    result = await optimization_service.get_resource_allocation_plan()
    
    assert result["status"] == "success"
    assert "allocations" in result
    assert "total_resources" in result
    assert "optimization_opportunities" in result
    
    # Verify allocations
    allocations = result["allocations"]
    assert len(allocations) == 2
    
    for allocation in allocations.values():
        assert "base_allocation" in allocation
        assert "recommended_allocation" in allocation
        assert "proportion" in allocation
        assert "scaling_limits" in allocation

async def test_get_scaling_recommendations(
    optimization_service,
    mock_analytics_service,
    sample_usage_prediction
):
    """Test scaling recommendations."""
    # Mock analytics service
    mock_analytics_service.return_value.predict_resource_usage.return_value = (
        sample_usage_prediction
    )

    # Test recommendation generation
    result = await optimization_service.get_scaling_recommendations("gpt-1")
    
    assert result["status"] == "success"
    assert "current_utilization" in result
    assert "scaling_recommendations" in result
    assert "trigger_points" in result
    assert "cost_impact" in result
    
    # Verify recommendations structure
    recommendations = result["scaling_recommendations"]
    for rec in recommendations:
        assert "type" in rec
        assert "urgency" in rec
        assert "scale_factor" in rec
        assert "reason" in rec

def test_calculate_optimization_plan(
    optimization_service,
    sample_usage_prediction,
    sample_performance_trends
):
    """Test optimization plan calculation."""
    plan = optimization_service._calculate_optimization_plan(
        sample_usage_prediction,
        sample_performance_trends,
        "balanced"
    )
    
    assert "recommended_allocation" in plan
    assert "buffer_strategy" in plan
    assert "scaling_threshold" in plan
    assert "growth_adjusted_allocation" in plan
    
    # Verify calculations
    assert plan["buffer_strategy"] == "moderate"
    assert plan["scaling_threshold"] == sample_usage_prediction["predictions"]["predicted_peak_usage"] * 0.8

def test_generate_scaling_recommendations(optimization_service):
    """Test scaling recommendation generation."""
    optimization_plan = {
        "recommended_allocation": 1.0,
        "scaling_threshold": 0.8,
        "growth_adjusted_allocation": 1.1
    }
    
    predictions = {
        "predicted_peak_usage": 0.85,  # Above threshold
        "growth_trend": 0.1
    }
    
    recommendations = optimization_service._generate_scaling_recommendations(
        optimization_plan,
        predictions
    )
    
    assert len(recommendations) == 2  # Should have immediate and planned scaling
    
    # Verify recommendation types
    rec_types = [r["type"] for r in recommendations]
    assert "immediate_scaling" in rec_types
    assert "planned_scaling" in rec_types

def test_estimate_improvements(optimization_service):
    """Test improvement estimation."""
    optimization_plan = {
        "recommended_allocation": 1.0,
        "scaling_threshold": 0.8
    }
    
    performance_trends = {
        "performance_score": 0.8
    }
    
    improvements = optimization_service._estimate_improvements(
        optimization_plan,
        performance_trends
    )
    
    assert "estimated_performance_score" in improvements
    assert "response_time_improvement" in improvements
    assert "reliability_improvement" in improvements
    assert "cost_efficiency_impact" in improvements
    
    # Verify estimates
    assert 0 <= improvements["estimated_performance_score"] <= 1
    assert improvements["estimated_performance_score"] > performance_trends["performance_score"]

def test_calculate_resource_allocations(optimization_service):
    """Test resource allocation calculation."""
    peak_demands = [
        ("gpt-1", 0.8),
        ("gpt-2", 0.6)
    ]
    total_resources = 1.4
    
    allocations = optimization_service._calculate_resource_allocations(
        peak_demands,
        total_resources
    )
    
    assert len(allocations) == 2
    
    # Verify allocation properties
    for gpt_id, allocation in allocations.items():
        assert allocation["base_allocation"] > 0
        assert allocation["recommended_allocation"] > allocation["base_allocation"]
        assert 0 < allocation["proportion"] <= 1
        assert allocation["scaling_limits"]["min"] < allocation["scaling_limits"]["max"]

def test_identify_optimization_opportunities(optimization_service):
    """Test optimization opportunity identification."""
    allocations = {
        "gpt-1": {
            "base_allocation": 0.8,
            "recommended_allocation": 1.0
        },
        "gpt-2": {
            "base_allocation": 0.4,
            "recommended_allocation": 0.5
        }
    }
    
    peak_demands = [
        ("gpt-1", 0.75),
        ("gpt-2", 0.2)  # Underutilized
    ]
    
    opportunities = optimization_service._identify_optimization_opportunities(
        allocations,
        peak_demands
    )
    
    assert len(opportunities) > 0
    
    # Verify opportunity structure
    for opportunity in opportunities:
        assert "type" in opportunity
        assert "severity" in opportunity
        if opportunity["type"] == "underutilization":
            assert "current_utilization" in opportunity
            assert "recommendation" in opportunity

def test_analyze_scaling_needs(optimization_service):
    """Test scaling needs analysis."""
    predictions = {
        "predicted_peak_usage": 0.85,  # High utilization
        "growth_trend": 0.15  # High growth
    }
    confidence_score = 0.8
    
    analysis = optimization_service._analyze_scaling_needs(
        predictions,
        confidence_score
    )
    
    assert "recommendations" in analysis
    assert "trigger_points" in analysis
    assert "confidence_level" in analysis
    
    # Verify recommendations
    recommendations = analysis["recommendations"]
    assert len(recommendations) == 2  # Should have both immediate and predictive scaling
    
    # Verify trigger points
    trigger_points = analysis["trigger_points"]
    assert len(trigger_points) == 2
    
    for trigger in trigger_points:
        assert "metric" in trigger
        assert "threshold" in trigger
        assert "action" in trigger
        assert "scale_factor" in trigger

def test_estimate_cost_impact(optimization_service):
    """Test cost impact estimation."""
    scaling_analysis = {
        "recommendations": [
            {
                "type": "vertical_scaling",
                "scale_factor": 1.5,
                "timeline": "immediate"
            },
            {
                "type": "predictive_scaling",
                "scale_factor": 1.2,
                "timeline": "7 days"
            }
        ],
        "confidence_level": 0.8
    }
    
    impact = optimization_service._estimate_cost_impact(scaling_analysis)
    
    assert "total_cost_impact" in impact
    assert "breakdown" in impact
    assert "optimization_potential" in impact
    
    # Verify breakdown
    breakdown = impact["breakdown"]
    assert len(breakdown) == 2
    
    for item in breakdown:
        assert "type" in item
        assert "cost_increase" in item
        assert "timeline" in item

def test_calculate_efficiency_impact(optimization_service):
    """Test efficiency impact calculation."""
    optimization_plan = {
        "scaling_threshold": 0.8,
        "recommended_allocation": 1.0
    }
    
    impact = optimization_service._calculate_efficiency_impact(optimization_plan)
    
    assert "resource_efficiency" in impact
    assert "cost_efficiency" in impact
    assert "optimization_ratio" in impact
    
    # Verify metrics
    assert 0 <= impact["resource_efficiency"] <= 1
    assert 0 <= impact["cost_efficiency"] <= 1
    assert impact["optimization_ratio"] >= 1.0

def test_calculate_optimization_potential(optimization_service):
    """Test optimization potential calculation."""
    total_cost = 100.0
    scaling_analysis = {
        "confidence_level": 0.8
    }
    
    potential = optimization_service._calculate_optimization_potential(
        total_cost,
        scaling_analysis
    )
    
    assert "potential_savings" in potential
    assert "confidence_level" in potential
    assert "optimization_methods" in potential
    
    # Verify optimization methods
    methods = potential["optimization_methods"]
    assert len(methods) == 2
    
    total_savings_potential = sum(
        method["savings_potential"]
        for method in methods
    )
    assert total_savings_potential == potential["potential_savings"] 