from typing import Dict, Any, Optional
import openai
from sqlalchemy.orm import Session
from app.dashboard.services.tool_registry_service import ToolRegistryService
from app.dashboard.services.gpt_coordination_service import GPTCoordinationService

class GPTFunctionService:
    def __init__(self, db: Session):
        self.db = db
        self.tool_registry = ToolRegistryService(db)
        self.gpt_coordinator = GPTCoordinationService(db)

    async def process_user_command(self, user_id: str, command: str) -> Dict[str, Any]:
        # Get available tool schemas for the user
        tool_schemas = self.tool_registry.get_tool_function_schemas(user_id)
        
        # Get GPT context for the user
        context = await self.gpt_coordinator.get_user_context(user_id)
        
        # Call OpenAI with the command and available tools
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "You are an AI dashboard assistant. Use the available tools to help the user."},
                {"role": "user", "content": command}
            ],
            functions=tool_schemas,
            function_call="auto"
        )
        
        # Process the response
        message = response.choices[0].message
        
        if message.function_call:
            # Execute the function call
            function_name = message.function_call.name
            function_args = message.function_call.arguments
            
            # Route to the appropriate tool
            result = await self._execute_function_call(function_name, function_args)
            
            # Get a natural language response about the result
            follow_up = await openai.ChatCompletion.acreate(
                model="gpt-4-0613",
                messages=[
                    {"role": "system", "content": "You are an AI dashboard assistant. Explain the result of the tool execution."},
                    {"role": "user", "content": f"Tool {function_name} returned: {result}"}
                ]
            )
            
            return {
                "action": function_name,
                "result": result,
                "explanation": follow_up.choices[0].message.content
            }
        else:
            return {
                "response": message.content
            }

    async def _execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        # This is a placeholder - implement actual function routing here
        # You would typically have a mapping of function names to actual API endpoints
        # or service methods
        pass

    async def suggest_tools(self, user_id: str, context: str) -> Dict[str, Any]:
        # Get available tools
        available_tools = self.tool_registry.get_user_tools(user_id)
        
        # Get GPT suggestion
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "You are an AI dashboard assistant. Suggest relevant tools based on the user's context."},
                {"role": "user", "content": f"Based on this context: {context}, which tools would be helpful?"}
            ]
        )
        
        return {
            "suggestion": response.choices[0].message.content,
            "available_tools": [tool.name for tool in available_tools]
        } 