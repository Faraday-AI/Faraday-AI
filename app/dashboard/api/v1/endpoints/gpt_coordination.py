"""
GPT Coordination API endpoints for the Faraday AI Dashboard.
"""

from typing import Optional, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from ....services.gpt_coordination_service import GPTCoordinationService
from ....models.gpt_models import GPTCategory

router = APIRouter()

@router.post("/context/initialize")
async def initialize_context(
    user_id: str,
    primary_gpt_id: str,
    context_data: Dict,
    name: Optional[str] = None,
    description: Optional[str] = None,
    include_metadata: bool = Query(True, description="Include context metadata"),
    include_active: bool = Query(True, description="Include active GPTs"),
    include_validation: bool = Query(True, description="Include validation results"),
    include_performance: bool = Query(True, description="Include performance metrics"),
    db: Session = Depends(get_db)
):
    """
    Initialize a new context for GPT coordination.
    
    Args:
        user_id: The ID of the user
        primary_gpt_id: The ID of the primary GPT
        context_data: Initial context data
        name: Optional name for the context
        description: Optional description for the context
        include_metadata: Whether to include context metadata
        include_active: Whether to include active GPTs
        include_validation: Whether to include validation results
        include_performance: Whether to include performance metrics
    """
    coordination_service = GPTCoordinationService(db)
    result = await coordination_service.initialize_context(
        user_id=user_id,
        primary_gpt_id=primary_gpt_id,
        context_data=context_data,
        name=name,
        description=description
    )
    
    if not include_metadata:
        result.pop("name", None)
        result.pop("description", None)
    
    if not include_active:
        result.pop("active_gpts", None)
    
    if include_validation:
        result["validation"] = {
            "subscription": await coordination_service.validate_gpt_subscription(user_id, primary_gpt_id),
            "data_compatibility": await coordination_service.validate_data_compatibility(context_data)
        }
    
    if include_performance:
        result["performance"] = {
            "initialization_time": result["created_at"],
            "context_size": len(str(context_data)),
            "gpt_capabilities": await coordination_service.get_gpt_capabilities(primary_gpt_id)
        }
    
    return result

@router.post("/context/{context_id}/add-gpt")
async def add_gpt_to_context(
    context_id: str,
    gpt_id: str,
    role: str,
    include_history: bool = Query(False, description="Include interaction history"),
    include_metadata: bool = Query(True, description="Include role metadata"),
    include_validation: bool = Query(True, description="Include validation results"),
    include_performance: bool = Query(True, description="Include performance metrics"),
    db: Session = Depends(get_db)
):
    """
    Add a GPT to an existing context.
    
    Args:
        context_id: The ID of the context
        gpt_id: The ID of the GPT to add
        role: The role of the GPT in the context
        include_history: Whether to include interaction history
        include_metadata: Whether to include role metadata
        include_validation: Whether to include validation results
        include_performance: Whether to include performance metrics
    """
    coordination_service = GPTCoordinationService(db)
    result = await coordination_service.add_gpt_to_context(
        context_id=context_id,
        gpt_id=gpt_id,
        role=role
    )
    
    if include_history:
        result["interaction_history"] = await coordination_service.get_context_history(
            context_id=context_id,
            gpt_id=gpt_id
        )
    
    if not include_metadata:
        result.pop("role", None)
    
    if include_validation:
        result["validation"] = {
            "gpt_authorization": await coordination_service.validate_gpt_in_context(context_id, gpt_id),
            "role_compatibility": await coordination_service.validate_role_compatibility(gpt_id, role)
        }
    
    if include_performance:
        result["performance"] = {
            "join_time": result.get("timestamp"),
            "context_size": await coordination_service.get_context_size(context_id),
            "gpt_capabilities": await coordination_service.get_gpt_capabilities(gpt_id)
        }
    
    return result

@router.post("/context/{context_id}/share")
async def share_context(
    context_id: str,
    source_gpt_id: str,
    target_gpt_id: str,
    shared_data: Dict,
    metadata: Optional[Dict] = None,
    include_validation: bool = Query(True, description="Include validation results"),
    include_history: bool = Query(False, description="Include sharing history"),
    include_performance: bool = Query(True, description="Include performance metrics"),
    db: Session = Depends(get_db)
):
    """
    Share context between GPTs.
    
    Args:
        context_id: The ID of the context
        source_gpt_id: The ID of the source GPT
        target_gpt_id: The ID of the target GPT
        shared_data: The data to share
        metadata: Optional metadata for the sharing
        include_validation: Whether to include validation results
        include_history: Whether to include sharing history
        include_performance: Whether to include performance metrics
    """
    coordination_service = GPTCoordinationService(db)
    result = await coordination_service.share_context(
        context_id=context_id,
        source_gpt_id=source_gpt_id,
        target_gpt_id=target_gpt_id,
        shared_data=shared_data,
        metadata=metadata
    )
    
    if include_validation:
        result["validation"] = {
            "source_gpt": await coordination_service.validate_gpt_in_context(context_id, source_gpt_id),
            "target_gpt": await coordination_service.validate_gpt_in_context(context_id, target_gpt_id),
            "data_compatibility": await coordination_service.validate_data_compatibility(shared_data)
        }
    
    if include_history:
        result["sharing_history"] = await coordination_service.get_context_history(
            context_id=context_id,
            gpt_id=source_gpt_id,
            interaction_type="share"
        )
    
    if include_performance:
        result["performance"] = {
            "share_time": result["shared_at"],
            "data_size": len(str(shared_data)),
            "latency": await coordination_service.calculate_sharing_latency(
                context_id,
                source_gpt_id,
                target_gpt_id
            )
        }
    
    return result

@router.get("/context/{context_id}/history")
async def get_context_history(
    context_id: str,
    gpt_id: Optional[str] = None,
    interaction_type: Optional[str] = None,
    include_metadata: bool = Query(True, description="Include interaction metadata"),
    include_content: bool = Query(True, description="Include interaction content"),
    include_summary: bool = Query(True, description="Include context summary"),
    include_performance: bool = Query(True, description="Include performance metrics"),
    db: Session = Depends(get_db)
):
    """
    Get the history of interactions in a context.
    
    Args:
        context_id: The ID of the context
        gpt_id: Optional GPT ID to filter interactions
        interaction_type: Optional interaction type to filter
        include_metadata: Whether to include interaction metadata
        include_content: Whether to include interaction content
        include_summary: Whether to include context summary
        include_performance: Whether to include performance metrics
    """
    coordination_service = GPTCoordinationService(db)
    result = {
        "history": await coordination_service.get_context_history(
            context_id=context_id,
            gpt_id=gpt_id,
            interaction_type=interaction_type
        )
    }
    
    if not include_metadata:
        for interaction in result["history"]:
            interaction.pop("metadata", None)
    
    if not include_content:
        for interaction in result["history"]:
            interaction.pop("content", None)
    
    if include_summary:
        result["summary"] = await coordination_service.get_context_summary(context_id)
    
    if include_performance:
        result["performance"] = {
            "total_interactions": len(result["history"]),
            "interaction_types": await coordination_service.get_interaction_types(context_id),
            "average_latency": await coordination_service.calculate_average_latency(context_id),
            "gpt_activity": await coordination_service.get_gpt_activity(context_id)
        }
    
    return result

@router.put("/context/{context_id}/update")
async def update_context(
    context_id: str,
    gpt_id: str,
    update_data: Dict,
    metadata: Optional[Dict] = None,
    include_validation: bool = Query(True, description="Include validation results"),
    include_history: bool = Query(False, description="Include update history"),
    include_performance: bool = Query(True, description="Include performance metrics"),
    db: Session = Depends(get_db)
):
    """
    Update context data.
    
    Args:
        context_id: The ID of the context
        gpt_id: The ID of the GPT making the update
        update_data: The data to update
        metadata: Optional metadata for the update
        include_validation: Whether to include validation results
        include_history: Whether to include update history
        include_performance: Whether to include performance metrics
    """
    coordination_service = GPTCoordinationService(db)
    result = await coordination_service.update_context(
        context_id=context_id,
        gpt_id=gpt_id,
        update_data=update_data,
        metadata=metadata
    )
    
    if include_validation:
        result["validation"] = {
            "gpt_authorization": await coordination_service.validate_gpt_in_context(context_id, gpt_id),
            "data_compatibility": await coordination_service.validate_data_compatibility(update_data)
        }
    
    if include_history:
        result["update_history"] = await coordination_service.get_context_history(
            context_id=context_id,
            gpt_id=gpt_id,
            interaction_type="update"
        )
    
    if include_performance:
        result["performance"] = {
            "update_time": result["updated_at"],
            "data_size": len(str(update_data)),
            "context_size": await coordination_service.get_context_size(context_id),
            "update_latency": await coordination_service.calculate_update_latency(context_id, gpt_id)
        }
    
    return result

@router.post("/context/{context_id}/close")
async def close_context(
    context_id: str,
    summary: Optional[Dict] = None,
    metadata: Optional[Dict] = None,
    include_history: bool = Query(True, description="Include final history"),
    include_summary: bool = Query(True, description="Include context summary"),
    include_performance: bool = Query(True, description="Include performance metrics"),
    db: Session = Depends(get_db)
):
    """
    Close a context.
    
    Args:
        context_id: The ID of the context to close
        summary: Optional summary of the context
        metadata: Optional metadata for the closure
        include_history: Whether to include final history
        include_summary: Whether to include context summary
        include_performance: Whether to include performance metrics
    """
    coordination_service = GPTCoordinationService(db)
    result = await coordination_service.close_context(
        context_id=context_id,
        summary=summary,
        metadata=metadata
    )
    
    if include_history:
        result["final_history"] = await coordination_service.get_context_history(context_id)
    
    if include_summary:
        result["context_summary"] = await coordination_service.get_context_summary(context_id)
    
    if include_performance:
        result["performance"] = {
            "total_duration": await coordination_service.calculate_context_duration(context_id),
            "total_interactions": len(result.get("final_history", [])),
            "gpt_activity": await coordination_service.get_gpt_activity(context_id),
            "context_size": await coordination_service.get_context_size(context_id)
        }
    
    return result

@router.get("/context/active")
async def get_active_contexts(
    user_id: str,
    gpt_id: Optional[str] = None,
    include_metadata: bool = Query(True, description="Include context metadata"),
    include_gpts: bool = Query(True, description="Include active GPTs"),
    include_summary: bool = Query(True, description="Include context summaries"),
    include_performance: bool = Query(True, description="Include performance metrics"),
    db: Session = Depends(get_db)
):
    """
    Get active contexts for a user.
    
    Args:
        user_id: The ID of the user
        gpt_id: Optional GPT ID to filter contexts
        include_metadata: Whether to include context metadata
        include_gpts: Whether to include active GPTs
        include_summary: Whether to include context summaries
        include_performance: Whether to include performance metrics
    """
    coordination_service = GPTCoordinationService(db)
    result = {
        "active_contexts": await coordination_service.get_active_contexts(
            user_id=user_id,
            gpt_id=gpt_id
        )
    }
    
    if not include_metadata:
        for context in result["active_contexts"]:
            context.pop("name", None)
            context.pop("description", None)
    
    if not include_gpts:
        for context in result["active_contexts"]:
            context.pop("active_gpts", None)
    
    if include_summary:
        result["summaries"] = {
            context["id"]: await coordination_service.get_context_summary(context["id"])
            for context in result["active_contexts"]
        }
    
    if include_performance:
        result["performance"] = {
            "total_contexts": len(result["active_contexts"]),
            "context_metrics": {
                context["id"]: {
                    "duration": await coordination_service.calculate_context_duration(context["id"]),
                    "interactions": len(await coordination_service.get_context_history(context["id"])),
                    "gpt_count": len(context.get("active_gpts", [])),
                    "context_size": await coordination_service.get_context_size(context["id"])
                }
                for context in result["active_contexts"]
            }
        }
    
    return result

@router.get("/context/{context_id}/validation")
async def validate_context(
    context_id: str,
    include_gpt_validation: bool = Query(True, description="Include GPT validation"),
    include_data_validation: bool = Query(True, description="Include data validation"),
    include_performance_validation: bool = Query(True, description="Include performance validation"),
    db: Session = Depends(get_db)
):
    """
    Validate a context's state and performance.
    
    Args:
        context_id: The ID of the context to validate
        include_gpt_validation: Whether to include GPT validation
        include_data_validation: Whether to include data validation
        include_performance_validation: Whether to include performance validation
    """
    coordination_service = GPTCoordinationService(db)
    result = {}
    
    if include_gpt_validation:
        result["gpt_validation"] = {
            "active_gpts": await coordination_service.get_active_gpts(context_id),
            "subscription_status": await coordination_service.validate_subscriptions(context_id),
            "role_compatibility": await coordination_service.validate_roles(context_id)
        }
    
    if include_data_validation:
        result["data_validation"] = {
            "context_data": await coordination_service.validate_context_data(context_id),
            "shared_data": await coordination_service.validate_shared_data(context_id),
            "data_compatibility": await coordination_service.validate_data_compatibility(
                await coordination_service.get_context_data(context_id)
            )
        }
    
    if include_performance_validation:
        result["performance_validation"] = {
            "latency": await coordination_service.calculate_average_latency(context_id),
            "throughput": await coordination_service.calculate_throughput(context_id),
            "error_rate": await coordination_service.calculate_error_rate(context_id),
            "resource_usage": await coordination_service.calculate_resource_usage(context_id)
        }
    
    return result

@router.get("/context/{context_id}/performance")
async def get_context_performance(
    context_id: str,
    include_metrics: bool = Query(True, description="Include performance metrics"),
    include_trends: bool = Query(True, description="Include performance trends"),
    include_benchmarks: bool = Query(True, description="Include performance benchmarks"),
    db: Session = Depends(get_db)
):
    """
    Get detailed performance metrics for a context.
    
    Args:
        context_id: The ID of the context
        include_metrics: Whether to include current metrics
        include_trends: Whether to include performance trends
        include_benchmarks: Whether to include performance benchmarks
    """
    coordination_service = GPTCoordinationService(db)
    result = {}
    
    if include_metrics:
        result["metrics"] = {
            "latency": await coordination_service.calculate_average_latency(context_id),
            "throughput": await coordination_service.calculate_throughput(context_id),
            "error_rate": await coordination_service.calculate_error_rate(context_id),
            "resource_usage": await coordination_service.calculate_resource_usage(context_id),
            "context_size": await coordination_service.get_context_size(context_id),
            "interaction_count": len(await coordination_service.get_context_history(context_id))
        }
    
    if include_trends:
        result["trends"] = {
            "latency_trend": await coordination_service.get_latency_trend(context_id),
            "throughput_trend": await coordination_service.get_throughput_trend(context_id),
            "error_trend": await coordination_service.get_error_trend(context_id),
            "resource_trend": await coordination_service.get_resource_trend(context_id)
        }
    
    if include_benchmarks:
        result["benchmarks"] = {
            "latency_benchmark": await coordination_service.get_latency_benchmark(context_id),
            "throughput_benchmark": await coordination_service.get_throughput_benchmark(context_id),
            "error_benchmark": await coordination_service.get_error_benchmark(context_id),
            "resource_benchmark": await coordination_service.get_resource_benchmark(context_id)
        }
    
    return result

@router.get("/context/{context_id}/analysis")
async def analyze_context(
    context_id: str,
    include_patterns: bool = Query(True, description="Include interaction patterns"),
    include_relationships: bool = Query(True, description="Include GPT relationships"),
    include_efficiency: bool = Query(True, description="Include efficiency metrics"),
    include_insights: bool = Query(True, description="Include contextual insights"),
    db: Session = Depends(get_db)
):
    """
    Analyze a context's interactions and relationships.
    
    Args:
        context_id: The ID of the context to analyze
        include_patterns: Whether to include interaction patterns
        include_relationships: Whether to include GPT relationships
        include_efficiency: Whether to include efficiency metrics
        include_insights: Whether to include contextual insights
    """
    coordination_service = GPTCoordinationService(db)
    result = {}
    
    if include_patterns:
        result["patterns"] = {
            "interaction_patterns": await coordination_service.analyze_interaction_patterns(context_id),
            "data_flow_patterns": await coordination_service.analyze_data_flow_patterns(context_id),
            "role_patterns": await coordination_service.analyze_role_patterns(context_id),
            "temporal_patterns": await coordination_service.analyze_temporal_patterns(context_id)
        }
    
    if include_relationships:
        result["relationships"] = {
            "gpt_relationships": await coordination_service.analyze_gpt_relationships(context_id),
            "data_dependencies": await coordination_service.analyze_data_dependencies(context_id),
            "role_dependencies": await coordination_service.analyze_role_dependencies(context_id),
            "interaction_network": await coordination_service.analyze_interaction_network(context_id)
        }
    
    if include_efficiency:
        result["efficiency"] = {
            "communication_efficiency": await coordination_service.analyze_communication_efficiency(context_id),
            "data_transfer_efficiency": await coordination_service.analyze_data_transfer_efficiency(context_id),
            "role_efficiency": await coordination_service.analyze_role_efficiency(context_id),
            "resource_efficiency": await coordination_service.analyze_resource_efficiency(context_id)
        }
    
    if include_insights:
        result["insights"] = {
            "context_insights": await coordination_service.generate_context_insights(context_id),
            "performance_insights": await coordination_service.generate_performance_insights(context_id),
            "optimization_insights": await coordination_service.generate_optimization_insights(context_id),
            "risk_insights": await coordination_service.generate_risk_insights(context_id)
        }
    
    return result

@router.get("/context/{context_id}/coordination")
async def get_coordination_metrics(
    context_id: str,
    include_synchronization: bool = Query(True, description="Include synchronization metrics"),
    include_collaboration: bool = Query(True, description="Include collaboration metrics"),
    include_consistency: bool = Query(True, description="Include consistency metrics"),
    include_quality: bool = Query(True, description="Include quality metrics"),
    db: Session = Depends(get_db)
):
    """
    Get detailed coordination metrics for a context.
    
    Args:
        context_id: The ID of the context
        include_synchronization: Whether to include synchronization metrics
        include_collaboration: Whether to include collaboration metrics
        include_consistency: Whether to include consistency metrics
        include_quality: Whether to include quality metrics
    """
    coordination_service = GPTCoordinationService(db)
    result = {}
    
    if include_synchronization:
        result["synchronization"] = {
            "state_sync": await coordination_service.analyze_state_synchronization(context_id),
            "data_sync": await coordination_service.analyze_data_synchronization(context_id),
            "role_sync": await coordination_service.analyze_role_synchronization(context_id),
            "timing_sync": await coordination_service.analyze_timing_synchronization(context_id)
        }
    
    if include_collaboration:
        result["collaboration"] = {
            "gpt_collaboration": await coordination_service.analyze_gpt_collaboration(context_id),
            "role_collaboration": await coordination_service.analyze_role_collaboration(context_id),
            "data_collaboration": await coordination_service.analyze_data_collaboration(context_id),
            "task_collaboration": await coordination_service.analyze_task_collaboration(context_id)
        }
    
    if include_consistency:
        result["consistency"] = {
            "state_consistency": await coordination_service.analyze_state_consistency(context_id),
            "data_consistency": await coordination_service.analyze_data_consistency(context_id),
            "role_consistency": await coordination_service.analyze_role_consistency(context_id),
            "behavior_consistency": await coordination_service.analyze_behavior_consistency(context_id)
        }
    
    if include_quality:
        result["quality"] = {
            "interaction_quality": await coordination_service.analyze_interaction_quality(context_id),
            "data_quality": await coordination_service.analyze_data_quality(context_id),
            "role_quality": await coordination_service.analyze_role_quality(context_id),
            "coordination_quality": await coordination_service.analyze_coordination_quality(context_id)
        }
    
    return result

@router.get("/context/{context_id}/optimization")
async def get_optimization_metrics(
    context_id: str,
    include_efficiency: bool = Query(True, description="Include efficiency metrics"),
    include_resource: bool = Query(True, description="Include resource metrics"),
    include_performance: bool = Query(True, description="Include performance metrics"),
    include_quality: bool = Query(True, description="Include quality metrics"),
    db: Session = Depends(get_db)
):
    """
    Get optimization metrics for a context.
    
    Args:
        context_id: The ID of the context
        include_efficiency: Whether to include efficiency metrics
        include_resource: Whether to include resource metrics
        include_performance: Whether to include performance metrics
        include_quality: Whether to include quality metrics
    """
    coordination_service = GPTCoordinationService(db)
    result = {}
    
    if include_efficiency:
        result["efficiency"] = {
            "communication_efficiency": await coordination_service.analyze_communication_efficiency(context_id),
            "data_transfer_efficiency": await coordination_service.analyze_data_transfer_efficiency(context_id),
            "role_efficiency": await coordination_service.analyze_role_efficiency(context_id),
            "resource_efficiency": await coordination_service.analyze_resource_efficiency(context_id)
        }
    
    if include_resource:
        result["resource"] = {
            "resource_usage": await coordination_service.analyze_resource_usage(context_id),
            "resource_allocation": await coordination_service.analyze_resource_allocation(context_id),
            "resource_optimization": await coordination_service.analyze_resource_optimization(context_id),
            "resource_potential": await coordination_service.analyze_resource_potential(context_id)
        }
    
    if include_performance:
        result["performance"] = {
            "latency": await coordination_service.analyze_latency(context_id),
            "throughput": await coordination_service.analyze_throughput(context_id),
            "scalability": await coordination_service.analyze_scalability(context_id),
            "reliability": await coordination_service.analyze_reliability(context_id)
        }
    
    if include_quality:
        result["quality"] = {
            "interaction_quality": await coordination_service.analyze_interaction_quality(context_id),
            "data_quality": await coordination_service.analyze_data_quality(context_id),
            "role_quality": await coordination_service.analyze_role_quality(context_id),
            "coordination_quality": await coordination_service.analyze_coordination_quality(context_id)
        }
    
    return result

@router.get("/context/{context_id}/monitoring")
async def get_monitoring_metrics(
    context_id: str,
    include_health: bool = Query(True, description="Include health metrics"),
    include_performance: bool = Query(True, description="Include performance metrics"),
    include_activity: bool = Query(True, description="Include activity metrics"),
    include_alerts: bool = Query(True, description="Include alert metrics"),
    db: Session = Depends(get_db)
):
    """
    Get monitoring metrics for a context.
    
    Args:
        context_id: The ID of the context
        include_health: Whether to include health metrics
        include_performance: Whether to include performance metrics
        include_activity: Whether to include activity metrics
        include_alerts: Whether to include alert metrics
    """
    coordination_service = GPTCoordinationService(db)
    result = {}
    
    if include_health:
        result["health"] = {
            "system_health": await coordination_service.monitor_system_health(context_id),
            "gpt_health": await coordination_service.monitor_gpt_health(context_id),
            "data_health": await coordination_service.monitor_data_health(context_id),
            "coordination_health": await coordination_service.monitor_coordination_health(context_id)
        }
    
    if include_performance:
        result["performance"] = {
            "latency": await coordination_service.monitor_latency(context_id),
            "throughput": await coordination_service.monitor_throughput(context_id),
            "resource_usage": await coordination_service.monitor_resource_usage(context_id),
            "error_rates": await coordination_service.monitor_error_rates(context_id)
        }
    
    if include_activity:
        result["activity"] = {
            "interaction_activity": await coordination_service.monitor_interaction_activity(context_id),
            "data_activity": await coordination_service.monitor_data_activity(context_id),
            "gpt_activity": await coordination_service.monitor_gpt_activity(context_id),
            "role_activity": await coordination_service.monitor_role_activity(context_id)
        }
    
    if include_alerts:
        result["alerts"] = {
            "health_alerts": await coordination_service.get_health_alerts(context_id),
            "performance_alerts": await coordination_service.get_performance_alerts(context_id),
            "activity_alerts": await coordination_service.get_activity_alerts(context_id),
            "coordination_alerts": await coordination_service.get_coordination_alerts(context_id)
        }
    
    return result 