"""
Content Generation Service
Handles content generation requests: images, PowerPoint, Word, PDF, Excel documents.
Uses focused prompt and function calling for efficient content creation.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from openai import OpenAI
import logging
import json
import asyncio

from app.services.pe.specialized_services.base_specialized_service import BaseSpecializedService
from app.dashboard.services.gpt_function_service import GPTFunctionService
from app.dashboard.services.widget_function_schemas import WidgetFunctionSchemas

logger = logging.getLogger(__name__)


class ContentGenerationService(BaseSpecializedService):
    """
    Specialized service for content generation (images, documents).
    Handles requests for generating images, PowerPoint, Word, PDF, Excel files.
    Uses focused prompt and function calling for efficient processing.
    """
    
    def __init__(self, db: Session, openai_client: OpenAI):
        super().__init__(db, openai_client)
        self.service_name = "ContentGenerationService"
    
    def get_system_prompt(self) -> str:
        """Load the focused content generation prompt."""
        try:
            from app.core.prompt_loader import load_raw_module
            return load_raw_module("specialized_content_generation.txt")
        except Exception as e:
            logger.warning(f"⚠️ Could not load specialized content generation prompt: {e}")
            # Fallback to focused prompt
            return """You are Jasper's Content Generation Specialist. You help users create:
- Images and artwork using DALL-E
- PowerPoint presentations
- Word documents
- PDF documents
- Excel spreadsheets

When users request content creation, use the available functions to generate the content.
Always confirm what the user wants before generating, and provide helpful guidance."""
    
    def get_supported_intents(self) -> List[str]:
        """Content generation service handles all content creation requests."""
        return [
            "content_generation",
            "generate_image",
            "create_powerpoint",
            "create_presentation",
            "create_word",
            "create_document",
            "create_pdf",
            "create_excel",
            "create_spreadsheet",
            "generate_artwork",
            "create_slides",
            "make_presentation",
            "make_document"
        ]
    
    def get_model(self) -> str:
        """Use gpt-4-turbo for content generation (needs function calling support and large context window)."""
        import os
        model = os.getenv("JASPER_MAIN_MODEL", "gpt-4-turbo")
        # Force gpt-4-turbo (not preview) for content generation to ensure 600k TPM limit
        if model in ["gpt-4", "gpt-4-turbo-preview"]:
            logger.warning(f"⚠️ JASPER_MAIN_MODEL is set to '{model}'. Forcing 'gpt-4-turbo' for content generation (600k TPM limit).")
            model = "gpt-4-turbo"
        return model
    
    def extract_widget_data(self, response_text: str, intent: str, original_message: str = "") -> Dict[str, Any]:
        """
        Extract widget data from response.
        Content generation may return function results with widget_data.
        """
        # Widget data is extracted from function results, not from response text
        # This is handled in the process() method
        return {
            "type": "content_generation",
            "data": {"response": response_text}
        }
    
    def process(self, user_request: str, context: dict = None) -> dict:
        """
        Process content generation request using function calling.
        Uses asyncio to bridge sync/async gap for GPTFunctionService.
        
        Args:
            user_request: User's request message
            context: Optional context dictionary
            
        Returns:
            Dictionary with response data including generated content
        """
        if context is None:
            context = {}
        
        # Run async processing in sync context
        # Check if we're already in an async context (event loop running)
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, we need to run in a thread
            import concurrent.futures
            import threading
            
            # Create a new event loop in a thread
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(self._process_async(user_request, context))
                finally:
                    new_loop.close()
            
            # Run in a thread pool
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result(timeout=300)  # 5 minute timeout
        except RuntimeError:
            # No event loop running, we can use run_until_complete
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(self._process_async(user_request, context))
    
    async def _process_async(self, user_request: str, context: dict) -> dict:
        """Async implementation of process method."""
        # Get user_id from context
        teacher_id = context.get("teacher_id")
        user_id = str(teacher_id) if teacher_id else context.get("user_id", "guest")
        
        # Initialize GPTFunctionService
        gpt_function_service = GPTFunctionService(
            db=self.db,
            user_id=user_id
        )
        
        # Get content generation function schemas
        content_schemas = [
            schema for schema in WidgetFunctionSchemas.get_all_schemas()
            if schema.get("name") in [
                "generate_image",
                "create_powerpoint_presentation",
                "create_word_document",
                "create_pdf_document",
                "create_excel_spreadsheet",
                "search_and_embed_video",
                "search_and_embed_web_links"
            ]
        ]
        
        # Get user first name from context
        user_first_name = context.get("user_first_name")
        
        # Build system prompt with user name if available
        system_prompt = self.get_system_prompt()
        if user_first_name:
            system_prompt += f"\n\n🚨 USER NAME REQUIREMENT: The user's first name is {user_first_name}. You MUST use their name ({user_first_name}) in your response. This is MANDATORY."
        
        # Build messages from conversation history if available
        # Preserve conversation memory while filtering out large base64 data to prevent token limit errors
        messages = []
        conversation_messages_history = context.get("conversation_messages", [])
        if conversation_messages_history:
            # Use last 5 messages to preserve conversation context while preventing token bloat
            # But intelligently filter out base64 data while keeping text content
            for msg in conversation_messages_history[-5:]:
                content = msg.get("content", "")
                role = msg.get("role", "user")
                
                # Intelligently filter: preserve text content, remove base64 data
                if isinstance(content, str):
                    original_length = len(content)
                    
                    # Remove base64 image data patterns (data:image/png;base64,<very long string>)
                    import re
                    # Pattern to match base64 image data URLs (more aggressive - catches any long base64 string)
                    base64_pattern = r'data:image/[^;]+;base64,[A-Za-z0-9+/=\s]{500,}'
                    content = re.sub(base64_pattern, '[IMAGE_BASE64_DATA_EXCLUDED]', content)
                    
                    # Also catch standalone base64 strings (very long alphanumeric strings that look like base64)
                    # Base64 strings are typically 1000+ characters for images
                    standalone_base64_pattern = r'[A-Za-z0-9+/=]{2000,}'
                    content = re.sub(standalone_base64_pattern, '[LARGE_BASE64_STRING_EXCLUDED]', content)
                    
                    # Also check for JSON structures that might contain base64
                    # If content looks like JSON with base64, try to preserve structure but remove base64
                    if content.startswith('{') or content.startswith('['):
                        try:
                            # json is already imported at module level
                            parsed = json.loads(content)
                            # Recursively remove base64 from JSON
                            def remove_base64_from_obj(obj):
                                if isinstance(obj, dict):
                                    return {k: remove_base64_from_obj(v) for k, v in obj.items()}
                                elif isinstance(obj, list):
                                    return [remove_base64_from_obj(item) for item in obj]
                                elif isinstance(obj, str):
                                    # If string is very long and looks like base64, replace it
                                    if len(obj) > 1000 and re.match(r'^[A-Za-z0-9+/=]+$', obj):
                                        return '[BASE64_DATA_EXCLUDED]'
                                    return obj
                                return obj
                            cleaned = remove_base64_from_obj(parsed)
                            content = json.dumps(cleaned, indent=0)[:5000]  # Limit JSON size
                        except (json.JSONDecodeError, Exception):
                            # If JSON parsing fails, just use string filtering
                            pass
                    
                    # If content is still very long after base64 removal, truncate intelligently
                    # Be more aggressive to prevent token bloat
                    if len(content) > 5000:
                        # Keep first 500 chars (likely contains useful context) and last 200 chars
                        content = content[:500] + "...[LARGE_CONTENT_MIDDLE_EXCLUDED]..." + content[-200:]
                    # If content is moderately long, just truncate middle
                    elif len(content) > 2000:
                        content = content[:800] + "...[CONTENT_MIDDLE_TRUNCATED]..." + content[-300:]
                    
                    # Log if we significantly reduced content size
                    if original_length > len(content) * 2:
                        logger.debug(f"📉 Filtered conversation message: {original_length} -> {len(content)} chars")
                
                messages.append({
                    "role": role,
                    "content": content
                })
        
        # Always add current user request
        messages.append({
            "role": "user",
            "content": user_request
        })
        
        try:
            # Call OpenAI with function calling using async client
            from openai import AsyncOpenAI
            async_client = AsyncOpenAI(api_key=self.openai_client.api_key)
            
            # Initialize extracted content
            extracted_content = {
                "images": [],
                "file_content": None,
                "filename": None,
                "web_url": None,
                "file_id": None,
                "widget_data": None,
                "num_slides": None
            }
            
            # Build conversation messages for multi-turn function calling
            conversation_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages
            
            ai_response = None
            total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            max_iterations = 5  # Prevent infinite loops
            iteration = 0
            
            # Multi-turn function calling loop
            model_name = self.get_model()
            logger.info(f"🎨 ContentGenerationService: Using model '{model_name}' for content generation")
            
            while iteration < max_iterations:
                iteration += 1
                
                # Estimate token count (rough: 1 token ≈ 4 characters)
                total_chars = sum(len(str(msg.get("content", ""))) for msg in conversation_messages)
                estimated_tokens = total_chars // 4
                logger.info(f"🎨 ContentGenerationService: Iteration {iteration}, estimated tokens: ~{estimated_tokens}")
                
                # Make API call
                response = await async_client.chat.completions.create(
                    model=model_name,
                    messages=conversation_messages,
                    tools=[{"type": "function", "function": schema} for schema in content_schemas],
                    tool_choice="auto",
                    temperature=0.7
                )
                
                message = response.choices[0].message
                
                # Accumulate usage
                total_usage["prompt_tokens"] += response.usage.prompt_tokens
                total_usage["completion_tokens"] += response.usage.completion_tokens
                total_usage["total_tokens"] += response.usage.total_tokens
                
                # Create a summary of the assistant message for conversation (exclude large base64 data)
                message_summary = {"role": message.role}
                if message.content:
                    message_summary["content"] = message.content
                if message.tool_calls:
                    # Exclude tool call arguments to prevent token bloat
                    message_summary["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": "[ARGUMENTS_EXCLUDED_FOR_TOKEN_LIMIT]"  # Exclude arguments
                            }
                        } for tc in message.tool_calls
                    ]
                
                # Add assistant message summary to conversation (not full message)
                conversation_messages.append(message_summary)
                
                # If there's text content, use it as the final response
                if message.content:
                    ai_response = message.content
                
                # Handle function calls (new API uses tool_calls instead of function_call)
                if message.tool_calls:
                    # Execute all tool calls
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
                        
                        logger.info(f"🎨 ContentGenerationService: Executing function {function_name} (iteration {iteration})")
                        
                        # If this is create_word_document and we have images from previous calls, inject them
                        if function_name == "create_word_document" and extracted_content.get("images"):
                            # Inject image data into content_sections
                            if "content_sections" in function_args and isinstance(function_args["content_sections"], list):
                                # Find the first section and add the first image to it
                                if len(function_args["content_sections"]) > 0:
                                    first_image = extracted_content["images"][0]
                                    image_base64 = first_image.get("image") or first_image.get("base64_image")
                                    if image_base64:
                                        function_args["content_sections"][0]["image_base64"] = image_base64
                                        logger.info("✅ Injected image data into create_word_document call")
                        
                        # Execute the function
                        result = await gpt_function_service._execute_function_call(
                            function_name=function_name,
                            arguments=function_args,
                            user_id=user_id
                        )
                        
                        # Check if function execution failed
                        if isinstance(result, dict) and result.get("status") == "error":
                            error_msg = result.get("error", "Unknown error")
                            logger.error(f"❌ Function {function_name} failed: {error_msg}")
                            # Continue to next iteration - let AI handle the error
                        
                        # Create a summary of the result for conversation (exclude large base64 data to avoid token limits)
                        result_summary = {}
                        if isinstance(result, dict):
                            # Copy all fields except large base64 data
                            for key, value in result.items():
                                if key in ["image", "base64_image", "file_content"]:
                                    # Don't include large base64 data in conversation - it causes token limit errors
                                    result_summary[key] = "[BASE64_DATA_AVAILABLE]"
                                elif key == "images" and isinstance(value, list):
                                    # For images array, create summary without base64
                                    result_summary[key] = [
                                        {
                                            k: (v if k not in ["image", "base64_image"] else "[BASE64_DATA_AVAILABLE]")
                                            for k, v in img.items()
                                        } if isinstance(img, dict) else img
                                        for img in value
                                    ]
                                else:
                                    result_summary[key] = value
                        else:
                            result_summary = result
                        
                        # Add function result summary to conversation for next iteration (without large base64)
                        # Keep tool result very minimal to prevent token bloat
                        tool_result_content = json.dumps(result_summary) if not isinstance(result_summary, str) else result_summary
                        # Limit tool result size to prevent token bloat (max 2000 chars)
                        if len(tool_result_content) > 2000:
                            # Truncate but keep structure
                            if isinstance(result_summary, dict):
                                # Keep only essential fields
                                minimal_result = {
                                    "success": result_summary.get("success", True),
                                    "message": result_summary.get("message", "")[:500] if result_summary.get("message") else "",
                                    "filename": result_summary.get("filename", "")[:100] if result_summary.get("filename") else ""
                                }
                                tool_result_content = json.dumps(minimal_result)
                            else:
                                tool_result_content = tool_result_content[:2000] + "...[TRUNCATED]"
                        
                        conversation_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result_content
                        })
                        
                        # Store the full result (with base64) separately for later use
                        # Only store successful results (skip errors)
                        if isinstance(result, dict) and result.get("status") != "error":
                            if result.get("images"):
                                extracted_content["images"].extend(result.get("images", []))
                            elif result.get("image") and function_name == "generate_image":
                                # Single image result from generate_image
                                extracted_content["images"].append({
                                    "image": result.get("image"),
                                    "url": result.get("url"),
                                    "prompt": result.get("prompt", ""),
                                    "filename": result.get("filename", "generated_image.png")
                                })
                            
                            if result.get("file_content"):
                                extracted_content["file_content"] = result.get("file_content")
                                extracted_content["filename"] = result.get("filename")
                            if result.get("web_url"):
                                extracted_content["web_url"] = result.get("web_url")
                                extracted_content["file_id"] = result.get("file_id")
                                if result.get("filename"):
                                    extracted_content["filename"] = result.get("filename")
                            if result.get("widget_data"):
                                # Merge widget_data if multiple functions create widgets
                                if extracted_content.get("widget_data"):
                                    # If we already have widget_data, prefer the document one over image one
                                    if result.get("widget_data", {}).get("type") == "generated-document":
                                        # Merge images from previous widget_data into the document widget_data
                                        existing_widget_data = extracted_content.get("widget_data", {})
                                        new_widget_data = result.get("widget_data", {})
                                        
                                        # If existing widget_data has images, merge them into the document widget_data
                                        if existing_widget_data.get("data", {}).get("images"):
                                            if not new_widget_data.get("data"):
                                                new_widget_data["data"] = {}
                                            if not new_widget_data["data"].get("images"):
                                                new_widget_data["data"]["images"] = []
                                            new_widget_data["data"]["images"].extend(existing_widget_data["data"]["images"])
                                        
                                        # Also merge any images from extracted_content["images"]
                                        if extracted_content.get("images"):
                                            if not new_widget_data.get("data"):
                                                new_widget_data["data"] = {}
                                            if not new_widget_data["data"].get("images"):
                                                new_widget_data["data"]["images"] = []
                                            new_widget_data["data"]["images"].extend(extracted_content["images"])
                                        
                                        extracted_content["widget_data"] = new_widget_data
                                    else:
                                        # Image widget_data - keep it but we'll merge images into document later
                                        extracted_content["widget_data"] = result.get("widget_data")
                                else:
                                    extracted_content["widget_data"] = result.get("widget_data")
                            if result.get("num_slides"):
                                extracted_content["num_slides"] = result.get("num_slides")
                else:
                    # No more tool calls, we're done
                    break
            
            # Get natural language explanation if we don't have one
            if not ai_response:
                # Check if we have a document (preferred) or just images
                if extracted_content.get("file_content") or extracted_content.get("web_url"):
                    doc_type = "document"
                    if extracted_content.get("filename"):
                        ext = extracted_content["filename"].split('.')[-1].lower()
                        if ext == "docx":
                            doc_type = "Word document"
                        elif ext == "pptx":
                            doc_type = "PowerPoint presentation"
                        elif ext == "pdf":
                            doc_type = "PDF document"
                        elif ext == "xlsx":
                            doc_type = "Excel spreadsheet"
                    ai_response = f"I've created your {doc_type}! You can download it or access it via OneDrive if it was uploaded."
                elif extracted_content.get("images"):
                    ai_response = "I've generated the image for you! You can download it or view it in the chat."
                else:
                    # If we have no content, something went wrong
                    ai_response = "I encountered an issue while generating the content. Please try again or provide more details about what you'd like me to create."
            
            # Get usage metadata
            usage_metadata = {
                "prompt_tokens": total_usage["prompt_tokens"],
                "completion_tokens": total_usage["completion_tokens"],
                "total_tokens": total_usage["total_tokens"],
                "model": self.get_model()
            }
            
            # Build response with extracted content
            # If we have a document widget_data, merge images into it
            widget_data = extracted_content.get("widget_data")
            if widget_data and widget_data.get("type") == "generated-document" and extracted_content.get("images"):
                # Ensure widget_data has a data field
                if not widget_data.get("data"):
                    widget_data["data"] = {}
                # Merge images into document widget_data
                if not widget_data["data"].get("images"):
                    widget_data["data"]["images"] = []
                widget_data["data"]["images"].extend(extracted_content["images"])
                logger.info(f"✅ Merged {len(extracted_content['images'])} image(s) into document widget_data")
            
            response_data = {
                "response": ai_response or "Content generation completed successfully.",
                "widget_data": widget_data,
                "usage": usage_metadata
            }
            
            # Include extracted content for chat display
            if extracted_content.get("images"):
                response_data["images"] = extracted_content["images"]
            if extracted_content.get("file_content"):
                response_data["file_content"] = extracted_content["file_content"]
                response_data["filename"] = extracted_content["filename"]
            if extracted_content.get("web_url"):
                response_data["web_url"] = extracted_content["web_url"]
                response_data["file_id"] = extracted_content["file_id"]
            if extracted_content.get("num_slides"):
                response_data["num_slides"] = extracted_content["num_slides"]
            
            logger.info(f"✅ ContentGenerationService: Generated content successfully")
            
            return response_data
            
        except Exception as e:
            logger.error(f"❌ ContentGenerationService: Error processing request: {e}", exc_info=True)
            # Return error response
            return {
                "response": f"I encountered an error while generating content: {str(e)}. Please try again.",
                "widget_data": None,
                "usage": {"total_tokens": 0}
            }

