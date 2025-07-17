"""
Compatibility API endpoints for the Faraday AI Dashboard.
"""

from typing import Optional, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from ....services.compatibility_service import CompatibilityService
from ....models.gpt_models import GPTCategory, GPTType
from ....schemas.compatibility_schemas import (
    CompatibilityCheck,
    CompatibleGPTs,
    IntegrationValidation,
    CompatibilityDashboard,
    DependencyAnalysis,
    VersionCompatibility,
    ResourceRequirements
)

router = APIRouter()

@router.get("/check/{gpt_id}", response_model=CompatibilityCheck)
async def check_compatibility(
    gpt_id: str,
    target_environment: Optional[Dict] = None,
    include_details: bool = Query(True, description="Include detailed check results"),
    include_impact: bool = Query(True, description="Include impact analysis"),
    include_recommendations: bool = Query(True, description="Include recommendations"),
    db: Session = Depends(get_db)
):
    """
    Check compatibility of a GPT with target environment.
    
    Args:
        gpt_id: The ID of the GPT to check
        target_environment: Optional target environment specifications
        include_details: Whether to include detailed check results
        include_impact: Whether to include impact analysis
        include_recommendations: Whether to include recommendations
    """
    compatibility_service = CompatibilityService(db)
    result = await compatibility_service.check_compatibility(
        gpt_id=gpt_id,
        target_environment=target_environment
    )
    
    if include_details:
        result["details"] = await compatibility_service.get_compatibility_details(
            gpt_id=gpt_id,
            target_environment=target_environment
        )
    
    if include_impact:
        result["impact"] = await compatibility_service.analyze_compatibility_impact(
            gpt_id=gpt_id,
            target_environment=target_environment
        )
    
    if include_recommendations:
        result["recommendations"] = await compatibility_service.get_compatibility_recommendations(
            gpt_id=gpt_id,
            target_environment=target_environment
        )
    
    return result

@router.get("/compatible/{gpt_id}", response_model=CompatibleGPTs)
async def get_compatible_gpts(
    gpt_id: str,
    category: Optional[GPTCategory] = None,
    include_metrics: bool = Query(True, description="Include compatibility metrics"),
    include_rankings: bool = Query(True, description="Include compatibility rankings"),
    include_improvements: bool = Query(True, description="Include improvement suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get list of GPTs compatible with the specified GPT.
    
    Args:
        gpt_id: The ID of the GPT to check against
        category: Optional category to filter compatible GPTs
        include_metrics: Whether to include compatibility metrics
        include_rankings: Whether to include compatibility rankings
        include_improvements: Whether to include improvement suggestions
    """
    compatibility_service = CompatibilityService(db)
    result = await compatibility_service.get_compatible_gpts(
        gpt_id=gpt_id,
        category=category
    )
    
    if include_metrics:
        result["metrics"] = await compatibility_service.get_compatibility_metrics(
            gpt_id=gpt_id,
            category=category
        )
    
    if include_rankings:
        result["rankings"] = await compatibility_service.get_compatibility_rankings(
            gpt_id=gpt_id,
            category=category
        )
    
    if include_improvements:
        result["improvements"] = await compatibility_service.get_compatibility_improvements(
            gpt_id=gpt_id,
            category=category
        )
    
    return result

@router.get("/validate-integration/{gpt_id}", response_model=IntegrationValidation)
async def validate_integration_requirements(
    gpt_id: str,
    integration_type: str = Query(..., description="Type of integration to validate"),
    include_requirements: bool = Query(True, description="Include detailed requirements"),
    include_validation: bool = Query(True, description="Include validation results"),
    include_recommendations: bool = Query(True, description="Include recommendations"),
    db: Session = Depends(get_db)
):
    """
    Validate integration requirements for a GPT.
    
    Args:
        gpt_id: The ID of the GPT to validate
        integration_type: Type of integration to validate
        include_requirements: Whether to include detailed requirements
        include_validation: Whether to include validation results
        include_recommendations: Whether to include recommendations
    """
    compatibility_service = CompatibilityService(db)
    result = await compatibility_service.validate_integration_requirements(
        gpt_id=gpt_id,
        integration_type=integration_type
    )
    
    if include_requirements:
        result["requirements"] = await compatibility_service.get_integration_requirements(
            gpt_id=gpt_id,
            integration_type=integration_type
        )
    
    if include_validation:
        result["validation"] = await compatibility_service.get_integration_validation(
            gpt_id=gpt_id,
            integration_type=integration_type
        )
    
    if include_recommendations:
        result["recommendations"] = await compatibility_service.get_integration_recommendations(
            gpt_id=gpt_id,
            integration_type=integration_type
        )
    
    return result

@router.get("/dashboard", response_model=CompatibilityDashboard)
async def get_compatibility_dashboard(
    category: Optional[GPTCategory] = None,
    include_trends: bool = Query(True, description="Include compatibility trends"),
    include_issues: bool = Query(True, description="Include compatibility issues"),
    include_recommendations: bool = Query(True, description="Include recommendations"),
    db: Session = Depends(get_db)
):
    """
    Get aggregated compatibility metrics for the dashboard.
    
    Args:
        category: Optional category to filter GPTs
        include_trends: Whether to include compatibility trends
        include_issues: Whether to include compatibility issues
        include_recommendations: Whether to include recommendations
    """
    compatibility_service = CompatibilityService(db)
    
    # Get all GPTs in the category
    gpts = db.query(GPTDefinition)
    if category:
        gpts = gpts.filter(GPTDefinition.category == category)
    gpts = gpts.all()
    
    # Collect compatibility metrics
    dashboard_data = {
        "overall_stats": {
            "total_gpts": len(gpts),
            "compatible_gpts": 0,
            "compatibility_issues": 0,
            "average_score": 0,
            "trends": {},
            "issues": {},
            "recommendations": {}
        },
        "gpt_metrics": {},
        "compatibility_issues": [],
        "recommendations": []
    }
    
    total_score = 0
    for gpt in gpts:
        # Check compatibility
        compatibility = await compatibility_service.check_compatibility(gpt.id)
        
        if compatibility["status"] == "success":
            score = compatibility["compatibility_score"]
            total_score += score
            
            dashboard_data["gpt_metrics"][gpt.id] = {
                "name": gpt.name,
                "category": gpt.category.value,
                "type": gpt.type.value,
                "compatibility_score": score,
                "checks": compatibility["checks"],
                "trends": await compatibility_service.get_gpt_compatibility_trends(gpt.id),
                "issues": await compatibility_service.get_gpt_compatibility_issues(gpt.id),
                "recommendations": await compatibility_service.get_gpt_compatibility_recommendations(gpt.id)
            }
            
            # Count compatible GPTs
            if score >= 0.8:  # High compatibility threshold
                dashboard_data["overall_stats"]["compatible_gpts"] += 1
            
            # Collect issues and recommendations
            for check_type, check in compatibility["checks"].items():
                if check["status"] == "failed":
                    dashboard_data["compatibility_issues"].extend([
                        {
                            "gpt_id": gpt.id,
                            "gpt_name": gpt.name,
                            "check_type": check_type,
                            **issue
                        }
                        for issue in check.get("compatibility_issues", [])
                    ])
            
            dashboard_data["recommendations"].extend([
                {
                    "gpt_id": gpt.id,
                    "gpt_name": gpt.name,
                    **rec
                }
                for rec in compatibility["recommendations"]
            ])
    
    # Update overall stats
    if gpts:
        dashboard_data["overall_stats"]["average_score"] = total_score / len(gpts)
        dashboard_data["overall_stats"]["compatibility_issues"] = len(
            dashboard_data["compatibility_issues"]
        )
    
    if include_trends:
        dashboard_data["overall_stats"]["trends"] = await compatibility_service.get_overall_compatibility_trends(
            category=category
        )
    
    if include_issues:
        dashboard_data["overall_stats"]["issues"] = await compatibility_service.get_overall_compatibility_issues(
            category=category
        )
    
    if include_recommendations:
        dashboard_data["overall_stats"]["recommendations"] = await compatibility_service.get_overall_compatibility_recommendations(
            category=category
        )
    
    return dashboard_data

@router.get("/dependencies/{gpt_id}", response_model=DependencyAnalysis)
async def analyze_dependencies(
    gpt_id: str,
    include_impact: bool = Query(True, description="Include dependency impact"),
    include_conflicts: bool = Query(True, description="Include dependency conflicts"),
    include_recommendations: bool = Query(True, description="Include recommendations"),
    db: Session = Depends(get_db)
):
    """
    Analyze dependencies for a GPT.
    
    Args:
        gpt_id: The ID of the GPT to analyze
        include_impact: Whether to include dependency impact
        include_conflicts: Whether to include dependency conflicts
        include_recommendations: Whether to include recommendations
    """
    compatibility_service = CompatibilityService(db)
    result = await compatibility_service.analyze_dependencies(gpt_id)
    
    if include_impact:
        result["impact"] = await compatibility_service.get_dependency_impact(gpt_id)
    
    if include_conflicts:
        result["conflicts"] = await compatibility_service.get_dependency_conflicts(gpt_id)
    
    if include_recommendations:
        result["recommendations"] = await compatibility_service.get_dependency_recommendations(gpt_id)
    
    return result

@router.get("/version/{gpt_id}", response_model=VersionCompatibility)
async def check_version_compatibility(
    gpt_id: str,
    include_updates: bool = Query(True, description="Include available updates"),
    include_impact: bool = Query(True, description="Include version impact"),
    include_recommendations: bool = Query(True, description="Include recommendations"),
    db: Session = Depends(get_db)
):
    """
    Check version compatibility for a GPT.
    
    Args:
        gpt_id: The ID of the GPT to check
        include_updates: Whether to include available updates
        include_impact: Whether to include version impact
        include_recommendations: Whether to include recommendations
    """
    compatibility_service = CompatibilityService(db)
    result = await compatibility_service.check_version_compatibility(gpt_id)
    
    if include_updates:
        result["updates"] = await compatibility_service.get_available_updates(gpt_id)
    
    if include_impact:
        result["impact"] = await compatibility_service.get_version_impact(gpt_id)
    
    if include_recommendations:
        result["recommendations"] = await compatibility_service.get_version_recommendations(gpt_id)
    
    return result

@router.get("/resources/{gpt_id}", response_model=ResourceRequirements)
async def check_resource_requirements(
    gpt_id: str,
    include_analysis: bool = Query(True, description="Include resource analysis"),
    include_optimization: bool = Query(True, description="Include optimization suggestions"),
    include_recommendations: bool = Query(True, description="Include recommendations"),
    db: Session = Depends(get_db)
):
    """
    Check resource requirements for a GPT.
    
    Args:
        gpt_id: The ID of the GPT to check
        include_analysis: Whether to include resource analysis
        include_optimization: Whether to include optimization suggestions
        include_recommendations: Whether to include recommendations
    """
    compatibility_service = CompatibilityService(db)
    result = await compatibility_service.check_resource_requirements(gpt_id)
    
    if include_analysis:
        result["analysis"] = await compatibility_service.get_resource_analysis(gpt_id)
    
    if include_optimization:
        result["optimization"] = await compatibility_service.get_resource_optimization(gpt_id)
    
    if include_recommendations:
        result["recommendations"] = await compatibility_service.get_resource_recommendations(gpt_id)
    
    return result 