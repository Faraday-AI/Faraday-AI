"""
GPT Context Management API

This module provides the API endpoints for managing GPT contexts
and coordination in the Faraday AI Dashboard.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dashboard.dependencies import get_current_user
from ....services.gpt_coordination_service import GPTCoordinationService
from ....schemas.context_schemas import (
    ContextCreate,
    ContextUpdate,
    AddGPTToContext,
    ShareContextData,
    ContextSummaryCreate,
    ContextHistoryFilter,
    ContextResponse,
    ContextInteractionResponse,
    SharedContextResponse,
    ContextSummaryResponse,
    ContextTemplateCreate
)

router = APIRouter()

@router.post("/contexts", response_model=ContextResponse)
async def create_context(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_data: ContextCreate
):
    """Create a new GPT context."""
    service = GPTCoordinationService(db)
    result = await service.initialize_context(
        user_id=current_user["id"],
        primary_gpt_id=context_data.primary_gpt_id,
        context_data=context_data.context_data,
        name=context_data.name,
        description=context_data.description
    )
    return result

@router.get("/contexts", response_model=List[ContextResponse])
async def get_active_contexts(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    gpt_id: Optional[str] = Query(None, description="Filter by GPT ID")
):
    """Get all active contexts for the current user."""
    service = GPTCoordinationService(db)
    return await service.get_active_contexts(
        user_id=current_user["id"],
        gpt_id=gpt_id
    )

@router.post("/contexts/{context_id}/gpts", response_model=ContextResponse)
async def add_gpt_to_context(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: str,
    gpt_data: AddGPTToContext
):
    """Add a GPT to an existing context."""
    service = GPTCoordinationService(db)
    return await service.add_gpt_to_context(
        context_id=context_id,
        gpt_id=gpt_data.gpt_id,
        role=gpt_data.role
    )

@router.post("/contexts/{context_id}/share", response_model=SharedContextResponse)
async def share_context(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: str,
    share_data: ShareContextData
):
    """Share context between GPTs."""
    service = GPTCoordinationService(db)
    return await service.share_context(
        context_id=context_id,
        source_gpt_id=share_data.source_gpt_id,
        target_gpt_id=share_data.target_gpt_id,
        shared_data=share_data.shared_data,
        metadata=share_data.metadata
    )

@router.get(
    "/contexts/{context_id}/history",
    response_model=List[ContextInteractionResponse]
)
async def get_context_history(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: str,
    filters: ContextHistoryFilter = Depends()
):
    """Get history of context interactions."""
    service = GPTCoordinationService(db)
    return await service.get_context_history(
        context_id=context_id,
        gpt_id=filters.gpt_id,
        interaction_type=filters.interaction_type
    )

@router.put("/contexts/{context_id}", response_model=ContextResponse)
async def update_context(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: str,
    update_data: ContextUpdate,
    gpt_id: str = Query(..., description="ID of the GPT making the update")
):
    """Update context with new information."""
    service = GPTCoordinationService(db)
    return await service.update_context(
        context_id=context_id,
        gpt_id=gpt_id,
        update_data=update_data.context_data or {},
        metadata=update_data.metadata
    )

@router.post(
    "/contexts/{context_id}/close",
    response_model=ContextSummaryResponse
)
async def close_context(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: str,
    summary_data: Optional[ContextSummaryCreate] = None
):
    """Close a context and optionally store summary."""
    service = GPTCoordinationService(db)
    return await service.close_context(
        context_id=context_id,
        summary=summary_data.summary if summary_data else None,
        metadata=summary_data.metadata if summary_data else None
    )

@router.get("/contexts/{context_id}/analysis")
async def analyze_context(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: str,
    include_metrics: bool = Query(True, description="Include performance metrics"),
    include_patterns: bool = Query(True, description="Include interaction patterns"),
    include_insights: bool = Query(True, description="Include context insights"),
    include_recommendations: bool = Query(True, description="Include optimization recommendations")
):
    """
    Analyze a context for insights and patterns.
    
    Args:
        context_id: The ID of the context to analyze
        include_metrics: Whether to include performance metrics
        include_patterns: Whether to include interaction patterns
        include_insights: Whether to include context insights
        include_recommendations: Whether to include optimization recommendations
    """
    service = GPTCoordinationService(db)
    return await service.analyze_context(
        context_id=context_id,
        include_metrics=include_metrics,
        include_patterns=include_patterns,
        include_insights=include_insights,
        include_recommendations=include_recommendations
    )

@router.post("/contexts/{context_id}/validate")
async def validate_context(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: str,
    validation_type: str = Query(..., regex="^(compatibility|integrity|performance|security)$"),
    validation_params: Optional[Dict[str, Any]] = None
):
    """
    Validate a context against specific criteria.
    
    Args:
        context_id: The ID of the context to validate
        validation_type: Type of validation to perform
        validation_params: Optional parameters for validation
    """
    service = GPTCoordinationService(db)
    return await service.validate_context(
        context_id=context_id,
        validation_type=validation_type,
        validation_params=validation_params
    )

@router.post("/contexts/{context_id}/backup")
async def backup_context(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: str,
    include_history: bool = Query(True, description="Include interaction history"),
    include_shared_data: bool = Query(True, description="Include shared context data")
):
    """
    Create a backup of a context.
    
    Args:
        context_id: The ID of the context to backup
        include_history: Whether to include interaction history
        include_shared_data: Whether to include shared context data
    """
    service = GPTCoordinationService(db)
    return await service.backup_context(
        context_id=context_id,
        include_history=include_history,
        include_shared_data=include_shared_data
    )

@router.post("/contexts/restore")
async def restore_context(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    backup_id: str,
    restore_options: Optional[Dict[str, Any]] = None
):
    """
    Restore a context from a backup.
    
    Args:
        backup_id: The ID of the backup to restore from
        restore_options: Optional restoration options
    """
    service = GPTCoordinationService(db)
    return await service.restore_context(
        backup_id=backup_id,
        restore_options=restore_options
    )

@router.get("/context-templates")
async def get_context_templates(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    category: Optional[str] = None,
    gpt_type: Optional[str] = None
):
    """
    Get available context templates.
    
    Args:
        category: Optional category to filter by
        gpt_type: Optional GPT type to filter by
    """
    service = GPTCoordinationService(db)
    return await service.get_context_templates(
        category=category,
        gpt_type=gpt_type
    )

@router.post("/context-templates")
async def create_context_template(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    template_data: ContextTemplateCreate
):
    """
    Create a new context template.
    
    Args:
        template_data: Template configuration data
    """
    service = GPTCoordinationService(db)
    return await service.create_context_template(
        name=template_data.name,
        description=template_data.description,
        category=template_data.category,
        configuration=template_data.configuration,
        metadata=template_data.metadata
    )

@router.post("/contexts/from-template")
async def create_context_from_template(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    template_id: str,
    context_data: Optional[Dict[str, Any]] = None
):
    """
    Create a new context from a template.
    
    Args:
        template_id: The ID of the template to use
        context_data: Optional additional context data
    """
    service = GPTCoordinationService(db)
    return await service.create_context_from_template(
        template_id=template_id,
        user_id=current_user["id"],
        context_data=context_data
    )

@router.get("/contexts/{context_id}/metrics")
async def get_context_metrics(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: str,
    metric_types: Optional[List[str]] = Query(None, description="Types of metrics to retrieve"),
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_trends: bool = Query(False, description="Include metric trends"),
    include_breakdown: bool = Query(False, description="Include metric breakdown")
):
    """
    Get performance metrics for a context.
    
    Args:
        context_id: The ID of the context
        metric_types: Optional list of metric types to retrieve
        time_range: Time range for metrics
        include_trends: Whether to include metric trends
        include_breakdown: Whether to include metric breakdown
    """
    service = GPTCoordinationService(db)
    return await service.get_context_metrics(
        context_id=context_id,
        metric_types=metric_types,
        time_range=time_range,
        include_trends=include_trends,
        include_breakdown=include_breakdown
    )

@router.get("/contexts/{context_id}/performance")
async def get_context_performance(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: str,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_gpt_metrics: bool = Query(True, description="Include GPT-specific metrics"),
    include_interaction_metrics: bool = Query(True, description="Include interaction metrics"),
    include_resource_metrics: bool = Query(True, description="Include resource usage metrics")
):
    """
    Get detailed performance data for a context.
    
    Args:
        context_id: The ID of the context
        time_range: Time range for performance data
        include_gpt_metrics: Whether to include GPT-specific metrics
        include_interaction_metrics: Whether to include interaction metrics
        include_resource_metrics: Whether to include resource usage metrics
    """
    service = GPTCoordinationService(db)
    return await service.get_context_performance(
        context_id=context_id,
        time_range=time_range,
        include_gpt_metrics=include_gpt_metrics,
        include_interaction_metrics=include_interaction_metrics,
        include_resource_metrics=include_resource_metrics
    )

@router.post("/contexts/{context_id}/optimize")
async def optimize_context(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: str,
    optimization_target: str = Query(..., regex="^(performance|efficiency|cost|reliability)$"),
    optimization_params: Optional[Dict[str, Any]] = None
):
    """
    Optimize a context for specific targets.
    
    Args:
        context_id: The ID of the context to optimize
        optimization_target: Target metric for optimization
        optimization_params: Optional optimization parameters
    """
    service = GPTCoordinationService(db)
    return await service.optimize_context(
        context_id=context_id,
        optimization_target=optimization_target,
        optimization_params=optimization_params
    ) 