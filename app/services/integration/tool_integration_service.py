rom typing import Dict, List, Any, Optional
import logging
import json
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    required_params: List[str]

class ToolIntegrationService:
    def __init__(self):
        self.registered_tools: Dict[str, ToolDefinition] = {}
        self.tool_history: List[Dict[str, Any]] = []

    async def register_tool(self, tool_definition: ToolDefinition) -> Dict[str, Any]:
        """Register a new tool for GPT to use."""
        try:
            self.registered_tools[tool_definition.name] = tool_definition
            return {
                "status": "success",
                "message": f"Tool {tool_definition.name} registered successfully"
            }
        except Exception as e:
            logger.error(f"Error registering tool: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available tools and their descriptions."""
        return [
            {
                "name": name,
                "description": tool.description,
                "parameters": tool.parameters,
                "required_params": tool.required_params
            }
            for name, tool in self.registered_tools.items()
        ]

    async def validate_tool_call(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a tool call before execution."""
        if tool_name not in self.registered_tools:
            return {
                "status": "error",
                "error": f"Tool {tool_name} not found"
            }

        tool = self.registered_tools[tool_name]
        missing_params = [
            param for param in tool.required_params
            if param not in parameters
        ]

        if missing_params:
            return {
                "status": "error",
                "error": f"Missing required parameters: {', '.join(missing_params)}"
            }

        return {"status": "success"}

    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        try:
            # Validate the tool call
            validation = await self.validate_tool_call(tool_name, parameters)
            if validation["status"] == "error":
                return validation

            # Record tool execution in history
            execution_record = {
                "tool": tool_name,
                "parameters": parameters,
                "context": context,
                "timestamp": "utcnow()"
            }
            self.tool_history.append(execution_record)

            # Here you would implement the actual tool execution logic
            # For now, we'll return a mock success response
            return {
                "status": "success",
                "result": f"Executed {tool_name} with parameters: {json.dumps(parameters)}"
            }
        except Exception as e:
            logger.error(f"Error executing tool: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def get_tool_history(
        self,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get history of tool executions."""
        history = self.tool_history
        if limit:
            history = history[-limit:]
        return history

    async def suggest_tools(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Suggest relevant tools based on user input and context."""
        # This would be enhanced with actual NLP/ML for better suggestions
        suggestions = []
        for tool in self.registered_tools.values():
            # Simple keyword matching for now
            if any(keyword in user_input.lower() 
                  for keyword in tool.description.lower().split()):
                suggestions.append({
                    "name": tool.name,
                    "description": tool.description,
                    "relevance": "high" if len(suggestions) < 3 else "medium"
                })
        return suggestions 
