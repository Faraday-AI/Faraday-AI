"""
GPT Manager API endpoints for the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....services.gpt_manager_service import GPTManagerService
from ....dependencies import get_db, get_current_user
from ....schemas.gpt_schemas import (
    ToolResponse,
    CommandRequest,
    CommandResponse,
    ToolMetrics,
    CommandMetrics,
    IntegrationResponse,
    ToolStatus,
    CommandHistory
)

router = APIRouter()

@router.get("/tools", response_model=List[str])
async def get_user_tools(
    include_metrics: bool = Query(False, description="Include tool metrics"),
    include_integrations: bool = Query(False, description="Include integration details"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of tools (GPTs) available to the current user.
    
    Args:
        include_metrics: Whether to include tool metrics
        include_integrations: Whether to include integration details
    """
    manager_service = GPTManagerService(db)
    tools = await manager_service.get_user_tools(current_user["id"])
    
    result = {"tools": tools}
    
    if include_metrics:
        result["metrics"] = {
            "tool_count": len(tools),
            "active_tools": await manager_service.get_active_tools(current_user["id"]),
            "tool_usage": await manager_service.get_tool_usage(current_user["id"]),
            "tool_performance": await manager_service.get_tool_performance(current_user["id"])
        }
    
    if include_integrations:
        result["integrations"] = {
            tool: await manager_service.get_tool_integrations(tool)
            for tool in tools
        }
    
    return result

@router.post("/tools/add", response_model=ToolResponse)
async def add_tool(
    tool_name: str = Query(..., description="Name of the GPT tool to add"),
    include_validation: bool = Query(True, description="Include validation results"),
    include_metrics: bool = Query(True, description="Include tool metrics"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Add a tool (GPT) to user's available tools.
    
    Args:
        tool_name: Name of the GPT tool to add
        include_validation: Whether to include validation results
        include_metrics: Whether to include tool metrics
    """
    manager_service = GPTManagerService(db)
    result = await manager_service.add_tool(current_user["id"], tool_name)
    
    if include_validation:
        result["validation"] = {
            "tool_exists": await manager_service.validate_tool_exists(tool_name),
            "subscription_valid": await manager_service.validate_subscription(current_user["id"], tool_name),
            "compatibility": await manager_service.validate_tool_compatibility(tool_name)
        }
    
    if include_metrics:
        result["metrics"] = {
            "tool_count": await manager_service.get_tool_count(current_user["id"]),
            "active_tools": await manager_service.get_active_tools(current_user["id"]),
            "tool_usage": await manager_service.get_tool_usage(current_user["id"])
        }
    
    return result

@router.post("/tools/remove", response_model=ToolResponse)
async def remove_tool(
    tool_name: str = Query(..., description="Name of the GPT tool to remove"),
    include_validation: bool = Query(True, description="Include validation results"),
    include_metrics: bool = Query(True, description="Include tool metrics"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Remove a tool (GPT) from user's available tools.
    
    Args:
        tool_name: Name of the GPT tool to remove
        include_validation: Whether to include validation results
        include_metrics: Whether to include tool metrics
    """
    manager_service = GPTManagerService(db)
    result = await manager_service.remove_tool(current_user["id"], tool_name)
    
    if include_validation:
        result["validation"] = {
            "tool_exists": await manager_service.validate_tool_exists(tool_name),
            "subscription_active": await manager_service.validate_subscription_active(current_user["id"], tool_name),
            "dependencies": await manager_service.check_tool_dependencies(tool_name)
        }
    
    if include_metrics:
        result["metrics"] = {
            "tool_count": await manager_service.get_tool_count(current_user["id"]),
            "active_tools": await manager_service.get_active_tools(current_user["id"]),
            "tool_usage": await manager_service.get_tool_usage(current_user["id"])
        }
    
    return result

@router.get("/tools/specs", response_model=List[Dict])
async def get_function_specs(
    include_metadata: bool = Query(True, description="Include function metadata"),
    include_validation: bool = Query(True, description="Include validation results"),
    include_metrics: bool = Query(True, description="Include function metrics"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get OpenAI function specifications for user's tools.
    
    Args:
        include_metadata: Whether to include function metadata
        include_validation: Whether to include validation results
        include_metrics: Whether to include function metrics
    """
    manager_service = GPTManagerService(db)
    specs = await manager_service.get_function_specs(current_user["id"])
    
    result = {"specs": specs}
    
    if include_metadata:
        result["metadata"] = {
            spec["name"]: await manager_service.get_function_metadata(spec["name"])
            for spec in specs
        }
    
    if include_validation:
        result["validation"] = {
            spec["name"]: await manager_service.validate_function_spec(spec)
            for spec in specs
        }
    
    if include_metrics:
        result["metrics"] = {
            spec["name"]: await manager_service.get_function_metrics(spec["name"])
            for spec in specs
        }
    
    return result

@router.post("/command", response_model=CommandResponse)
async def handle_command(
    command: CommandRequest,
    include_validation: bool = Query(True, description="Include validation results"),
    include_metrics: bool = Query(True, description="Include command metrics"),
    include_trace: bool = Query(False, description="Include command execution trace"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Handle a natural language command from the user.
    
    Args:
        command: The command request
        include_validation: Whether to include validation results
        include_metrics: Whether to include command metrics
        include_trace: Whether to include command execution trace
    """
    manager_service = GPTManagerService(db)
    result = await manager_service.handle_gpt_command(
        current_user["id"],
        command.command
    )
    
    if include_validation:
        result["validation"] = {
            "command_valid": await manager_service.validate_command(command.command),
            "tools_available": await manager_service.validate_tools_available(command.command),
            "permissions": await manager_service.validate_command_permissions(current_user["id"], command.command)
        }
    
    if include_metrics:
        result["metrics"] = {
            "execution_time": await manager_service.get_command_execution_time(command.command),
            "resource_usage": await manager_service.get_command_resource_usage(command.command),
            "success_rate": await manager_service.get_command_success_rate(command.command),
            "error_rate": await manager_service.get_command_error_rate(command.command)
        }
    
    if include_trace:
        result["trace"] = await manager_service.get_command_execution_trace(command.command)
    
    return result

@router.get("/tools/metrics", response_model=ToolMetrics)
async def get_tool_metrics(
    tool_name: Optional[str] = None,
    include_performance: bool = Query(True, description="Include performance metrics"),
    include_usage: bool = Query(True, description="Include usage metrics"),
    include_health: bool = Query(True, description="Include health metrics"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed metrics for tools.
    
    Args:
        tool_name: Optional specific tool name
        include_performance: Whether to include performance metrics
        include_usage: Whether to include usage metrics
        include_health: Whether to include health metrics
    """
    manager_service = GPTManagerService(db)
    result = {}
    
    if include_performance:
        result["performance"] = {
            "latency": await manager_service.get_tool_latency(tool_name),
            "throughput": await manager_service.get_tool_throughput(tool_name),
            "error_rate": await manager_service.get_tool_error_rate(tool_name),
            "success_rate": await manager_service.get_tool_success_rate(tool_name)
        }
    
    if include_usage:
        result["usage"] = {
            "request_count": await manager_service.get_tool_request_count(tool_name),
            "active_users": await manager_service.get_tool_active_users(tool_name),
            "resource_usage": await manager_service.get_tool_resource_usage(tool_name),
            "concurrency": await manager_service.get_tool_concurrency(tool_name)
        }
    
    if include_health:
        result["health"] = {
            "status": await manager_service.get_tool_status(tool_name),
            "availability": await manager_service.get_tool_availability(tool_name),
            "reliability": await manager_service.get_tool_reliability(tool_name),
            "alerts": await manager_service.get_tool_alerts(tool_name)
        }
    
    return result

@router.get("/command/metrics", response_model=CommandMetrics)
async def get_command_metrics(
    command_type: Optional[str] = None,
    include_performance: bool = Query(True, description="Include performance metrics"),
    include_usage: bool = Query(True, description="Include usage metrics"),
    include_quality: bool = Query(True, description="Include quality metrics"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed metrics for commands.
    
    Args:
        command_type: Optional specific command type
        include_performance: Whether to include performance metrics
        include_usage: Whether to include usage metrics
        include_quality: Whether to include quality metrics
    """
    manager_service = GPTManagerService(db)
    result = {}
    
    if include_performance:
        result["performance"] = {
            "execution_time": await manager_service.get_command_execution_time(command_type),
            "latency": await manager_service.get_command_latency(command_type),
            "throughput": await manager_service.get_command_throughput(command_type),
            "error_rate": await manager_service.get_command_error_rate(command_type)
        }
    
    if include_usage:
        result["usage"] = {
            "command_count": await manager_service.get_command_count(command_type),
            "user_count": await manager_service.get_command_user_count(command_type),
            "resource_usage": await manager_service.get_command_resource_usage(command_type),
            "concurrency": await manager_service.get_command_concurrency(command_type)
        }
    
    if include_quality:
        result["quality"] = {
            "success_rate": await manager_service.get_command_success_rate(command_type),
            "accuracy": await manager_service.get_command_accuracy(command_type),
            "satisfaction": await manager_service.get_command_satisfaction(command_type),
            "completion_rate": await manager_service.get_command_completion_rate(command_type)
        }
    
    return result

@router.get("/integrations", response_model=List[IntegrationResponse])
async def get_integrations(
    tool_name: Optional[str] = None,
    include_validation: bool = Query(True, description="Include validation results"),
    include_metrics: bool = Query(True, description="Include integration metrics"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get integrations for tools.
    
    Args:
        tool_name: Optional specific tool name
        include_validation: Whether to include validation results
        include_metrics: Whether to include integration metrics
    """
    manager_service = GPTManagerService(db)
    result = {}
    
    if tool_name:
        result["integrations"] = await manager_service.get_tool_integrations(tool_name)
    else:
        result["integrations"] = await manager_service.get_all_integrations(current_user["id"])
    
    if include_validation:
        result["validation"] = {
            integration["id"]: await manager_service.validate_integration(integration["id"])
            for integration in result["integrations"]
        }
    
    if include_metrics:
        result["metrics"] = {
            integration["id"]: await manager_service.get_integration_metrics(integration["id"])
            for integration in result["integrations"]
        }
    
    return result

@router.get("/tools/status", response_model=List[ToolStatus])
async def get_tool_status(
    tool_name: Optional[str] = None,
    include_dependencies: bool = Query(True, description="Include dependency status"),
    include_health: bool = Query(True, description="Include health metrics"),
    include_performance: bool = Query(True, description="Include performance metrics"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed status information for tools.
    
    Args:
        tool_name: Optional specific tool name
        include_dependencies: Whether to include dependency status
        include_health: Whether to include health metrics
        include_performance: Whether to include performance metrics
    """
    manager_service = GPTManagerService(db)
    result = {}
    
    if tool_name:
        result["status"] = await manager_service.get_tool_status(tool_name)
    else:
        tools = await manager_service.get_user_tools(current_user["id"])
        result["status"] = {
            tool: await manager_service.get_tool_status(tool)
            for tool in tools
        }
    
    if include_dependencies:
        result["dependencies"] = {
            tool: await manager_service.get_tool_dependencies(tool)
            for tool in (tools if not tool_name else [tool_name])
        }
    
    if include_health:
        result["health"] = {
            tool: {
                "availability": await manager_service.get_tool_availability(tool),
                "reliability": await manager_service.get_tool_reliability(tool),
                "alerts": await manager_service.get_tool_alerts(tool),
                "error_rate": await manager_service.get_tool_error_rate(tool)
            }
            for tool in (tools if not tool_name else [tool_name])
        }
    
    if include_performance:
        result["performance"] = {
            tool: {
                "latency": await manager_service.get_tool_latency(tool),
                "throughput": await manager_service.get_tool_throughput(tool),
                "concurrency": await manager_service.get_tool_concurrency(tool),
                "resource_usage": await manager_service.get_tool_resource_usage(tool)
            }
            for tool in (tools if not tool_name else [tool_name])
        }
    
    return result

@router.get("/command/history", response_model=List[CommandHistory])
async def get_command_history(
    tool_name: Optional[str] = None,
    command_type: Optional[str] = None,
    include_metrics: bool = Query(True, description="Include command metrics"),
    include_results: bool = Query(True, description="Include command results"),
    include_trace: bool = Query(False, description="Include execution trace"),
    limit: int = Query(100, description="Number of commands to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get command execution history.
    
    Args:
        tool_name: Optional specific tool name
        command_type: Optional specific command type
        include_metrics: Whether to include command metrics
        include_results: Whether to include command results
        include_trace: Whether to include execution trace
        limit: Number of commands to return
    """
    manager_service = GPTManagerService(db)
    result = {}
    
    result["history"] = await manager_service.get_command_history(
        current_user["id"],
        tool_name=tool_name,
        command_type=command_type,
        limit=limit
    )
    
    if include_metrics:
        result["metrics"] = {
            command["id"]: {
                "execution_time": await manager_service.get_command_execution_time(command["id"]),
                "resource_usage": await manager_service.get_command_resource_usage(command["id"]),
                "success_rate": await manager_service.get_command_success_rate(command["id"]),
                "error_rate": await manager_service.get_command_error_rate(command["id"])
            }
            for command in result["history"]
        }
    
    if include_results:
        result["results"] = {
            command["id"]: await manager_service.get_command_result(command["id"])
            for command in result["history"]
        }
    
    if include_trace:
        result["trace"] = {
            command["id"]: await manager_service.get_command_execution_trace(command["id"])
            for command in result["history"]
        }
    
    return result

@router.get("/tools/dependencies", response_model=Dict[str, List[str]])
async def get_tool_dependencies(
    tool_name: Optional[str] = None,
    include_status: bool = Query(True, description="Include dependency status"),
    include_metrics: bool = Query(True, description="Include dependency metrics"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get tool dependencies.
    
    Args:
        tool_name: Optional specific tool name
        include_status: Whether to include dependency status
        include_metrics: Whether to include dependency metrics
    """
    manager_service = GPTManagerService(db)
    result = {}
    
    if tool_name:
        result["dependencies"] = await manager_service.get_tool_dependencies(tool_name)
    else:
        tools = await manager_service.get_user_tools(current_user["id"])
        result["dependencies"] = {
            tool: await manager_service.get_tool_dependencies(tool)
            for tool in tools
        }
    
    if include_status:
        result["status"] = {
            tool: await manager_service.get_dependency_status(tool)
            for tool in (result["dependencies"].keys() if tool_name else tools)
        }
    
    if include_metrics:
        result["metrics"] = {
            tool: {
                "availability": await manager_service.get_dependency_availability(tool),
                "latency": await manager_service.get_dependency_latency(tool),
                "error_rate": await manager_service.get_dependency_error_rate(tool)
            }
            for tool in (result["dependencies"].keys() if tool_name else tools)
        }
    
    return result

@router.get("/tools/categories", response_model=Dict[str, List[str]])
async def get_tool_categories(
    include_metrics: bool = Query(True, description="Include category metrics"),
    include_tools: bool = Query(True, description="Include tools in each category"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get tool categories and their associated tools.
    
    Args:
        include_metrics: Whether to include category metrics
        include_tools: Whether to include tools in each category
    """
    manager_service = GPTManagerService(db)
    result = {}
    
    result["categories"] = await manager_service.get_tool_categories()
    
    if include_tools:
        result["tools"] = {
            category: await manager_service.get_tools_in_category(category)
            for category in result["categories"]
        }
    
    if include_metrics:
        result["metrics"] = {
            category: {
                "tool_count": await manager_service.get_category_tool_count(category),
                "active_tools": await manager_service.get_category_active_tools(category),
                "usage": await manager_service.get_category_usage(category)
            }
            for category in result["categories"]
        }
    
    return result 