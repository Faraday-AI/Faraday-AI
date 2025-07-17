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
import openai

from ..models.gpt_models import (
    GPTDefinition,
    DashboardGPTSubscription,
    GPTPerformance,
    GPTUsage,
    GPTAnalytics,
    GPTFeedback
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

    async def get_user_tools(self, user_id: str) -> List[str]:
        """Get list of tools (GPTs) available to a user."""
        try:
            if user_id in self.tool_registry:
                return self.tool_registry[user_id]

            subscriptions = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id,
                DashboardGPTSubscription.status == "active"
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
                status="active",
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
                subscription.status = "inactive"
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
                    GPTIntegration.gpt_definition_id == gpt.id,
                    GPTIntegration.status == "active"
                ).all()

                # Build function spec
                spec = {
                    "name": f"use_{gpt.type.value.lower()}",
                    "description": f"Use the {gpt.name} GPT for {gpt.type.value} tasks",
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
            # Get function specs for user's tools
            functions = await self.get_function_specs(user_id)

            # Get GPT response with function calling
            response = await openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": command}],
                functions=functions,
                function_call="auto"
            )

            # Handle function calls
            if response.choices[0].function_call:
                function_call = response.choices[0].function_call
                # Execute the function (implement your function routing logic here)
                result = await self._execute_function(
                    user_id,
                    function_call.name,
                    function_call.arguments
                )
                GPT_COMMAND_COUNT.labels(status="success").inc()
                return {
                    "status": "success",
                    "action": function_call.name,
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
                GPTDefinition.type == GPTType(gpt_type)
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
                GPTIntegration.status == "active"
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