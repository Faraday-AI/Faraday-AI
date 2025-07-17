from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.dashboard.models.tool_registry import Tool, UserTool
from app.dashboard.schemas.tool_registry import ToolCreate, ToolUpdate, UserToolCreate, UserToolUpdate
from fastapi import HTTPException
from datetime import datetime
import json
from jsonschema import validate, ValidationError

class ToolRegistryService:
    def __init__(self, db: Session):
        self.db = db

    def get_tool(self, tool_id: str) -> Tool:
        tool = self.db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        return tool

    def get_tools(self, skip: int = 0, limit: int = 100) -> List[Tool]:
        return self.db.query(Tool).offset(skip).limit(limit).all()

    def create_tool(self, tool_data: ToolCreate) -> Tool:
        # Validate function schema
        if tool_data.function_schema:
            self._validate_function_schema(tool_data.function_schema)
        
        # Validate configuration if provided
        if tool_data.configuration:
            self._validate_configuration(tool_data.configuration)
        
        tool = Tool(
            id=tool_data.id,
            name=tool_data.name,
            description=tool_data.description,
            category=tool_data.category,
            function_schema=tool_data.function_schema,
            is_active=tool_data.is_active,
            requires_approval=tool_data.requires_approval,
            version=tool_data.version,
            configuration=tool_data.configuration,
            validation_schema=tool_data.validation_schema,
            example_usage=tool_data.example_usage,
            rate_limit=tool_data.rate_limit,
            error_handling=tool_data.error_handling
        )
        self.db.add(tool)
        self.db.commit()
        self.db.refresh(tool)
        return tool

    def update_tool(self, tool_id: str, tool_data: ToolUpdate) -> Tool:
        tool = self.get_tool(tool_id)
        
        # Validate updates if provided
        if tool_data.function_schema:
            self._validate_function_schema(tool_data.function_schema)
        if tool_data.configuration:
            self._validate_configuration(tool_data.configuration)
        
        for field, value in tool_data.dict(exclude_unset=True).items():
            setattr(tool, field, value)
        
        tool.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(tool)
        return tool

    def delete_tool(self, tool_id: str) -> None:
        tool = self.get_tool(tool_id)
        self.db.delete(tool)
        self.db.commit()

    def get_user_tools(self, user_id: str) -> List[Tool]:
        return self.db.query(Tool).join(UserTool).filter(UserTool.user_id == user_id).all()

    def enable_tool_for_user(self, user_id: str, tool_id: str, settings: Optional[Dict] = None) -> UserTool:
        tool = self.get_tool(tool_id)
        user_tool = UserTool(
            user_id=user_id,
            tool_id=tool_id,
            settings=settings or {},
            last_used=datetime.utcnow()
        )
        self.db.add(user_tool)
        self.db.commit()
        self.db.refresh(user_tool)
        return user_tool

    def disable_tool_for_user(self, user_id: str, tool_id: str) -> None:
        user_tool = self.db.query(UserTool).filter(
            UserTool.user_id == user_id,
            UserTool.tool_id == tool_id
        ).first()
        if user_tool:
            self.db.delete(user_tool)
            self.db.commit()

    def _validate_function_schema(self, schema: Dict) -> None:
        """Validate the GPT function schema format."""
        required_fields = ["name", "description", "parameters"]
        for field in required_fields:
            if field not in schema:
                raise HTTPException(
                    status_code=400,
                    detail=f"Function schema missing required field: {field}"
                )
        
        if not isinstance(schema["parameters"], dict):
            raise HTTPException(
                status_code=400,
                detail="Function parameters must be a dictionary"
            )

    def _validate_configuration(self, config: Dict) -> None:
        """Validate tool configuration."""
        if not isinstance(config, dict):
            raise HTTPException(
                status_code=400,
                detail="Configuration must be a dictionary"
            )

    def get_tool_function_schema(self, tool_id: str) -> Dict:
        """Get the GPT function schema for a tool."""
        tool = self.get_tool(tool_id)
        if not tool.function_schema:
            raise HTTPException(
                status_code=404,
                detail="Function schema not found for this tool"
            )
        return tool.function_schema

    def validate_tool_call(self, tool_id: str, arguments: Dict, user_id: str) -> bool:
        """Validate a tool call against its schema and additional rules."""
        tool = self.get_tool(tool_id)
        user_tool = self.db.query(UserTool).filter(
            UserTool.user_id == user_id,
            UserTool.tool_id == tool_id
        ).first()

        # 1. Basic Tool State Validation
        if not tool.is_active:
            raise HTTPException(
                status_code=403,
                detail="Tool is not currently active"
            )

        if tool.requires_approval and not user_tool:
            raise HTTPException(
                status_code=403,
                detail="Tool requires approval before use"
            )

        # 2. Version Compatibility Validation
        if tool.version:
            try:
                # Split version into components (e.g., "1.2.3" -> [1, 2, 3])
                current_version = [int(x) for x in tool.version.split('.')]
                # TODO: Compare with system version or minimum required version
                # This could be expanded based on your versioning requirements
            except ValueError:
                raise HTTPException(
                    status_code=500,
                    detail="Invalid version format in tool configuration"
                )

        # 3. Configuration Validation
        if tool.configuration:
            try:
                # Validate configuration structure
                if not isinstance(tool.configuration, dict):
                    raise HTTPException(
                        status_code=500,
                        detail="Invalid configuration format"
                    )
                
                # Validate required configuration fields
                required_config = tool.configuration.get("required_fields", [])
                for field in required_config:
                    if field not in tool.configuration:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Missing required configuration field: {field}"
                        )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Configuration validation failed: {str(e)}"
                )

        # 4. Category-based Validation
        if tool.category:
            # Add category-specific validation rules
            if tool.category == "sensitive":
                # Example: Additional validation for sensitive operations
                if not user_tool or not user_tool.settings.get("sensitive_access", False):
                    raise HTTPException(
                        status_code=403,
                        detail="Additional permissions required for sensitive operations"
                    )

        # 5. User Settings Validation
        if user_tool and user_tool.settings:
            try:
                # Validate user settings against tool requirements
                if tool.configuration and "settings_schema" in tool.configuration:
                    validate(instance=user_tool.settings, schema=tool.configuration["settings_schema"])
            except ValidationError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid user settings: {str(e)}"
                )

        # 6. Rate Limit Validation
        if tool.rate_limit and user_tool:
            current_time = datetime.utcnow()
            if user_tool.rate_limit_reset and current_time > user_tool.rate_limit_reset:
                # Reset rate limit if period has passed
                user_tool.rate_limit_remaining = tool.rate_limit.get("limit", 0)
                user_tool.rate_limit_reset = current_time + tool.rate_limit.get("period", 3600)
            
            if user_tool.rate_limit_remaining <= 0:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again after {user_tool.rate_limit_reset}"
                )

        # 7. Schema Validation
        try:
            if tool.validation_schema:
                validate(instance=arguments, schema=tool.validation_schema)
            
            if tool.function_schema and "parameters" in tool.function_schema:
                function_schema = {
                    "type": "object",
                    "properties": tool.function_schema["parameters"],
                    "required": tool.function_schema.get("required", [])
                }
                validate(instance=arguments, schema=function_schema)
        except ValidationError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid tool call arguments: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error validating tool call: {str(e)}"
            )

        # 8. Error Handling Validation
        if tool.error_handling and user_tool:
            max_errors = tool.error_handling.get("max_errors", 0)
            if max_errors > 0 and user_tool.error_count >= max_errors:
                raise HTTPException(
                    status_code=403,
                    detail="Maximum error limit reached. Tool access temporarily disabled"
                )

        return True

    def update_tool_usage(self, user_id: str, tool_id: str, success: bool = True) -> None:
        """Update tool usage statistics."""
        user_tool = self.db.query(UserTool).filter(
            UserTool.user_id == user_id,
            UserTool.tool_id == tool_id
        ).first()
        
        if user_tool:
            user_tool.usage_count += 1
            user_tool.last_used = datetime.utcnow()
            if success:
                user_tool.last_success = datetime.utcnow()
                user_tool.error_count = 0
            else:
                user_tool.last_error = datetime.utcnow()
                user_tool.error_count += 1
            
            self.db.commit() 