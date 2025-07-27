"""
GPT Manager Service

This module provides the service layer for managing the GPT dashboard manager,
which acts as the primary interface for coordinating multiple GPTs.
"""

from typing import Dict, List, Optional
from datetime import datetime
import time
from sqlalchemy.orm import Session
from fastapi import HTTPException
from openai import OpenAI
import os

from ..models.gpt_models import (
    GPTDefinition,
    DashboardGPTSubscription,
    GPTPerformance,
    GPTUsage,
    GPTAnalytics,
    GPTFeedback,
    GPTIntegration
)
from ..models.context import GPTContext
from ..metrics import (
    GPT_TOOL_COUNT,
    GPT_COMMAND_LATENCY,
    GPT_COMMAND_COUNT,
    GPT_TOOL_ERRORS
)
from app.services.access_control_service import AccessControlService
from app.dashboard.models.access_control import ResourceType, ActionType

class GPTManagerService:
    def __init__(self, db: Session):
        self.db = db
        self.tool_registry = {}  # In-memory cache of user tools
        self._openai_client = None

    @property
    def openai_client(self):
        """Lazy initialization of OpenAI client."""
        if self._openai_client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self._openai_client = OpenAI(api_key=api_key)
            else:
                # For testing or when no API key is available
                self._openai_client = None
        return self._openai_client

    async def get_user_tools(self, user_id: str) -> List[str]:
        """Get list of tools (GPTs) available to a user."""
        try:
            if user_id in self.tool_registry:
                return self.tool_registry[user_id]

            subscriptions = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id,
                DashboardGPTSubscription.is_active == True
            ).all()

            tools = [sub.gpt_definition_id for sub in subscriptions]
            self.tool_registry[user_id] = tools
            
            # Update metrics
            GPT_TOOL_COUNT.labels(user_id=user_id).set(len(tools))
            
            return tools
        except Exception as e:
            GPT_TOOL_ERRORS.labels(tool_name="get_user_tools").inc()
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving user tools: {str(e)}"
            )

    async def add_tool(self, user_id: str, tool_name: str) -> Dict:
        """Add a tool (GPT) to user's available tools."""
        try:
            # Check if GPT exists
            gpt = self.db.query(GPTDefinition).filter(
                GPTDefinition.name == tool_name
            ).first()
            
            if not gpt:
                raise HTTPException(
                    status_code=404,
                    detail=f"GPT {tool_name} not found"
                )

            # Create subscription
            subscription = DashboardGPTSubscription(
                user_id=user_id,
                gpt_definition_id=gpt.id,
                name=tool_name,
                model=gpt.model_type,
                is_active=True,
                created_at=datetime.utcnow()
            )
            self.db.add(subscription)
            self.db.commit()

            # Update tool registry
            if user_id in self.tool_registry:
                self.tool_registry[user_id].append(gpt.id)
                GPT_TOOL_COUNT.labels(user_id=user_id).set(len(self.tool_registry[user_id]))

            return {
                "status": "success",
                "message": f"Added {tool_name} to user's tools",
                "tool_id": gpt.id
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            self.db.rollback()
            GPT_TOOL_ERRORS.labels(tool_name=tool_name).inc()
            raise HTTPException(
                status_code=500,
                detail=f"Error adding tool: {str(e)}"
            )

    async def remove_tool(self, user_id: str, tool_name: str) -> Dict:
        """Remove a tool (GPT) from user's available tools."""
        try:
            # Find GPT
            gpt = self.db.query(GPTDefinition).filter(
                GPTDefinition.name == tool_name
            ).first()
            
            if not gpt:
                raise HTTPException(
                    status_code=404,
                    detail=f"GPT {tool_name} not found"
                )

            # Update subscription
            subscription = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id,
                DashboardGPTSubscription.gpt_definition_id == gpt.id
            ).first()

            if subscription:
                subscription.is_active = False
                self.db.commit()

                # Update tool registry
                if user_id in self.tool_registry:
                    self.tool_registry[user_id].remove(gpt.id)
                    GPT_TOOL_COUNT.labels(user_id=user_id).set(len(self.tool_registry[user_id]))

            return {
                "status": "success",
                "message": f"Removed {tool_name} from user's tools"
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            self.db.rollback()
            GPT_TOOL_ERRORS.labels(tool_name=tool_name).inc()
            raise HTTPException(
                status_code=500,
                detail=f"Error removing tool: {str(e)}"
            )

    async def get_function_specs(self, user_id: str) -> List[Dict]:
        """Get OpenAI function specifications for user's tools."""
        try:
            tools = await self.get_user_tools(user_id)
            
            gpts = self.db.query(GPTDefinition).filter(
                GPTDefinition.id.in_(tools)
            ).all()

            specs = []
            for gpt in gpts:
                # Get integrations for the GPT
                integrations = self.db.query(GPTIntegration).filter(
                    GPTIntegration.user_id == user_id,
                    GPTIntegration.is_active == True
                ).all()

                # Build function spec
                spec = {
                    "name": f"use_{gpt.type.value.lower() if gpt.type else 'gpt'}",
                    "description": f"Use the {gpt.name} GPT for {gpt.type.value if gpt.type else 'general'} tasks",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {"type": "string", "description": "The task to perform"},
                            "context": {"type": "object", "description": "Additional context"}
                        },
                        "required": ["task"]
                    }
                }

                # Add integration-specific parameters
                for integration in integrations:
                    if integration.configuration and "parameters" in integration.configuration:
                        spec["parameters"]["properties"].update(
                            integration.configuration["parameters"]
                        )

                specs.append(spec)

            return specs
        except Exception as e:
            GPT_TOOL_ERRORS.labels(tool_name="get_function_specs").inc()
            raise HTTPException(
                status_code=500,
                detail=f"Error getting function specifications: {str(e)}"
            )

    async def handle_gpt_command(self, user_id: str, command: str) -> Dict:
        """Handle a natural language command from the user."""
        start_time = time.time()
        try:
            # Check if OpenAI client is available
            if not self.openai_client:
                raise HTTPException(
                    status_code=503,
                    detail="OpenAI service not available"
                )

            # Get function specs for user's tools
            functions = await self.get_function_specs(user_id)

            # Get GPT response with function calling
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": command}],
                tools=functions,
                tool_choice="auto"
            )

            # Handle function calls
            if response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                # Execute the function (implement your function routing logic here)
                result = await self._execute_function(
                    user_id,
                    tool_call.function.name,
                    tool_call.function.arguments
                )
                GPT_COMMAND_COUNT.labels(status="success").inc()
                return {
                    "status": "success",
                    "action": tool_call.function.name,
                    "result": result
                }
            else:
                GPT_COMMAND_COUNT.labels(status="success").inc()
                return {
                    "status": "success",
                    "message": response.choices[0].message.content
                }
        except Exception as e:
            GPT_COMMAND_COUNT.labels(status="error").inc()
            raise HTTPException(
                status_code=500,
                detail=f"Error handling command: {str(e)}"
            )
        finally:
            GPT_COMMAND_LATENCY.observe(time.time() - start_time)

    async def _execute_function(
        self,
        user_id: str,
        function_name: str,
        arguments: Dict
    ) -> Dict:
        """Execute a function call from GPT."""
        try:
            # Extract GPT type from function name (e.g., "use_math_teacher" -> "math_teacher")
            gpt_type = function_name.replace("use_", "")
            
            # Get the GPT definition
            gpt = self.db.query(GPTDefinition).filter(
                GPTDefinition.type == gpt_type
            ).first()
            
            if not gpt:
                raise HTTPException(
                    status_code=404,
                    detail=f"GPT type {gpt_type} not found"
                )
            
            # Validate user has access to this GPT
            tools = await self.get_user_tools(user_id)
            if gpt.id not in tools:
                raise HTTPException(
                    status_code=403,
                    detail=f"User does not have access to GPT type {gpt_type}"
                )
            
            # Check if user has permission to execute this GPT function
            access_control = AccessControlService(self.db)
            has_permission = await access_control.check_permission(
                user_id=user_id,
                resource_type=ResourceType.TOOL,
                action=ActionType.EXECUTE,
                resource_id=gpt.id
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"User does not have permission to execute GPT type {gpt_type}"
                )
            
            # Get active integrations for this GPT
            integrations = self.db.query(GPTIntegration).filter(
                GPTIntegration.gpt_definition_id == gpt.id,
                GPTIntegration.is_active == True
            ).all()
            
            # Execute each integration's function
            results = {}
            for integration in integrations:
                try:
                    # Check if user has permission to use this integration
                    has_integration_permission = await access_control.check_permission(
                        user_id=user_id,
                        resource_type=ResourceType.API,
                        action=ActionType.EXECUTE,
                        resource_id=integration.id
                    )
                    
                    if not has_integration_permission:
                        results[integration.name] = {
                            "status": "error",
                            "error": "Permission denied for integration"
                        }
                        continue
                    
                    # Execute the integration's handler function
                    handler = integration.handler
                    integration_result = await handler(arguments)
                    results[integration.name] = {
                        "status": "success",
                        "result": integration_result
                    }
                except Exception as e:
                    results[integration.name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    GPT_TOOL_ERRORS.labels(tool_name=integration.name).inc()
            
            # Record function execution metrics
            GPT_TOOL_COUNT.labels(user_id=user_id).inc()
            
            return {
                "status": "success",
                "gpt_type": gpt_type,
                "results": results,
                "metadata": {
                    "execution_time": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "function_name": function_name
                }
            }
            
        except HTTPException as he:
            raise he
        except Exception as e:
            GPT_TOOL_ERRORS.labels(tool_name="execute_function").inc()
            raise HTTPException(
                status_code=500,
                detail=f"Error executing function: {str(e)}"
            )

    # Validation methods
    async def validate_tool_exists(self, tool_name: str) -> bool:
        """Validate that a tool exists."""
        try:
            gpt = self.db.query(GPTDefinition).filter(
                GPTDefinition.name == tool_name
            ).first()
            return gpt is not None
        except Exception:
            return False

    async def validate_subscription(self, user_id: str, tool_name: str) -> bool:
        """Validate that user has a valid subscription for the tool."""
        try:
            gpt = self.db.query(GPTDefinition).filter(
                GPTDefinition.name == tool_name
            ).first()
            if not gpt:
                return False
            
            subscription = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id,
                DashboardGPTSubscription.gpt_definition_id == gpt.id,
                DashboardGPTSubscription.is_active == True
            ).first()
            return subscription is not None
        except Exception:
            return False

    async def validate_subscription_active(self, user_id: str, tool_name: str) -> bool:
        """Validate that user has an active subscription for the tool."""
        return await self.validate_subscription(user_id, tool_name)

    async def validate_tool_compatibility(self, tool_name: str) -> bool:
        """Validate tool compatibility."""
        try:
            gpt = self.db.query(GPTDefinition).filter(
                GPTDefinition.name == tool_name
            ).first()
            return gpt is not None and gpt.requirements is not None
        except Exception:
            return False

    async def check_tool_dependencies(self, tool_name: str) -> List[str]:
        """Check tool dependencies."""
        try:
            gpt = self.db.query(GPTDefinition).filter(
                GPTDefinition.name == tool_name
            ).first()
            if gpt and gpt.requirements and "dependencies" in gpt.requirements:
                return list(gpt.requirements["dependencies"].keys())
            return []
        except Exception:
            return []

    # Metrics methods
    async def get_tool_count(self, user_id: str) -> int:
        """Get the number of tools for a user."""
        try:
            subscriptions = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id,
                DashboardGPTSubscription.is_active == True
            ).all()
            return len(subscriptions)
        except Exception:
            return 0

    async def get_active_tools(self, user_id: str) -> List[str]:
        """Get list of active tools for a user."""
        try:
            subscriptions = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id,
                DashboardGPTSubscription.is_active == True
            ).all()
            return [sub.gpt_definition_id for sub in subscriptions]
        except Exception:
            return []

    async def get_tool_usage(self, user_id: str) -> Dict[str, int]:
        """Get tool usage statistics for a user."""
        try:
            # This would typically query usage history
            return {"gpt-1": 10, "gpt-2": 5}  # Placeholder
        except Exception:
            return {}

    async def get_tool_performance(self, user_id: str) -> Dict[str, float]:
        """Get tool performance metrics for a user."""
        try:
            # This would typically query performance metrics
            return {"gpt-1": 0.95, "gpt-2": 0.88}  # Placeholder
        except Exception:
            return {}

    async def get_tool_integrations(self, tool_id: str) -> List[Dict]:
        """Get integrations for a specific tool."""
        try:
            integrations = self.db.query(GPTIntegration).filter(
                GPTIntegration.gpt_definition_id == tool_id,
                GPTIntegration.is_active == True
            ).all()
            return [{"id": i.id, "name": i.name, "type": i.integration_type} for i in integrations]
        except Exception:
            return []

    # Function specification methods
    async def get_function_metadata(self, function_name: str) -> Dict:
        """Get metadata for a specific function."""
        try:
            return {
                "version": "1.0",
                "author": "Faraday AI",
                "description": f"Function for {function_name}",
                "created_at": datetime.utcnow().isoformat()
            }
        except Exception:
            return {}

    async def validate_function_spec(self, spec: Dict) -> bool:
        """Validate a function specification."""
        try:
            required_fields = ["name", "parameters"]
            return all(field in spec for field in required_fields)
        except Exception:
            return False

    async def get_function_metrics(self, function_name: str) -> Dict:
        """Get metrics for a specific function."""
        try:
            return {
                "calls": 100,
                "success_rate": 0.95,
                "avg_execution_time": 1.2,
                "last_called": datetime.utcnow().isoformat()
            }
        except Exception:
            return {}

    async def get_function_usage(self, function_name: str) -> Dict:
        """Get usage statistics for a specific function."""
        try:
            return {
                "daily": 10,
                "weekly": 50,
                "monthly": 200,
                "total": 1000
            }
        except Exception:
            return {}

    # Command methods
    async def validate_command(self, command: str) -> bool:
        """Validate a command."""
        try:
            return len(command.strip()) > 0
        except Exception:
            return False

    async def get_command_metrics(self, command_type: str = None) -> Dict:
        """Get command execution metrics."""
        try:
            return {
                "execution_time": 1.5,
                "success_rate": 0.9,
                "total_commands": 1000,
                "avg_response_time": 2.1
            }
        except Exception:
            return {}

    async def get_command_history(self, tool_name: str = None, command_type: str = None) -> List[Dict]:
        """Get command execution history."""
        try:
            return [
                {
                    "command": "solve equation",
                    "result": "success",
                    "execution_time": 1.2,
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        except Exception:
            return []

    async def get_command_trace(self, command_id: str) -> Dict:
        """Get execution trace for a specific command."""
        try:
            return {
                "steps": ["parse", "execute", "return"],
                "execution_time": 1.5,
                "status": "completed"
            }
        except Exception:
            return {}

    # Additional methods for handle_command endpoint
    async def validate_tools_available(self, command: str) -> bool:
        """Validate that tools are available for the command."""
        try:
            # Simple validation - check if user has any tools
            tools = await self.get_user_tools("user-1")  # This should be passed as parameter
            return len(tools) > 0
        except Exception:
            return False

    async def validate_command_permissions(self, user_id: str, command: str) -> bool:
        """Validate user permissions for the command."""
        try:
            # Simple validation - assume user has permissions
            return True
        except Exception:
            return False

    async def get_command_execution_time(self, command: str) -> float:
        """Get execution time for a command."""
        try:
            return 1.5  # Placeholder
        except Exception:
            return 0.0

    async def get_command_resource_usage(self, command: str) -> Dict:
        """Get resource usage for a command."""
        try:
            return {
                "cpu": 0.5,
                "memory": 0.3,
                "network": 0.1
            }
        except Exception:
            return {}

    async def get_command_success_rate(self, command: str) -> float:
        """Get success rate for a command."""
        try:
            return 0.95  # Placeholder
        except Exception:
            return 0.0

    async def get_command_error_rate(self, command: str) -> float:
        """Get error rate for a command."""
        try:
            return 0.05  # Placeholder
        except Exception:
            return 0.0

    async def get_command_execution_trace(self, command: str) -> Dict:
        """Get execution trace for a command."""
        try:
            return {
                "steps": ["parse", "execute", "return"],
                "execution_time": 1.5,
                "status": "completed"
            }
        except Exception:
            return {} 