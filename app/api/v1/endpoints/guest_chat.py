"""
Guest-friendly chat endpoint for dashboard.
Allows users to chat with AI assistant without requiring authentication.
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
from openai import OpenAI
from app.core.config import get_settings
from app.services.integration.twilio_service import get_twilio_service
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatMessageRequest(BaseModel):
    message: str
    context: Optional[List[Dict[str, str]]] = None

class ChatMessageResponse(BaseModel):
    response: str
    widgets: Optional[Dict[str, Any]] = None
    widget_data: Optional[Dict[str, Any]] = None

@router.post("/chat/message", response_model=ChatMessageResponse)
async def guest_chat_message(
    request: ChatMessageRequest,
    authorization: Optional[str] = Header(None)
) -> JSONResponse:
    """
    Send a message to the AI assistant (guest-friendly, no authentication required).
    This endpoint allows users to chat with the AI assistant without logging in.
    """
    try:
        settings = get_settings()
        
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured"
            )
        
        # Initialize OpenAI client
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Prepare messages for OpenAI
        messages = []
        
        # Add system prompt for Physical Education assistant
        system_prompt = """You are a helpful AI assistant for Physical Education teachers. 
You help create lesson plans, assessments, activities, and provide guidance for PE classes.
You are knowledgeable about physical education, health, fitness, and student development.
Be friendly, professional, and provide practical, actionable advice.

IMPORTANT CAPABILITIES:
- You can send SMS/text messages using the send_sms function when users ask you to send a text message
- When a user asks you to send a text message, you MUST:
  1. Ask for the phone number if not provided (in E.164 format like +1234567890)
  2. Ask for the message content if not provided
  3. Use the send_sms function to actually send the message
- Do NOT just repeat the user's request - actually perform the action using the available functions"""
        
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Define available functions for OpenAI
        functions = [
            {
                "type": "function",
                "function": {
                    "name": "send_sms",
                    "description": "Send an SMS/text message to a phone number using Twilio",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to_number": {
                                "type": "string",
                                "description": "The recipient's phone number in E.164 format (e.g., +1234567890). Must include country code."
                            },
                            "message": {
                                "type": "string",
                                "description": "The message content to send"
                            }
                        },
                        "required": ["to_number", "message"]
                    }
                }
            }
        ]
        
        # Add conversation context if provided
        if request.context:
            for ctx in request.context:
                if isinstance(ctx, dict) and 'role' in ctx and 'content' in ctx:
                    messages.append({
                        "role": ctx['role'],
                        "content": ctx['content']
                    })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        logger.info(f"Guest chat request: {len(messages)} messages in context")
        
        # Call OpenAI API with function calling
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            tools=[{"type": "function", "function": func["function"]} for func in functions],
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        ai_response = message.content
        
        # Handle function calls
        if message.tool_calls:
            logger.info(f"AI requested {len(message.tool_calls)} function calls")
            
            # Add assistant message with tool calls to conversation
            messages.append({
                "role": "assistant",
                "content": ai_response,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })
            
            # Execute function calls
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "send_sms":
                    twilio_service = get_twilio_service()
                    result = await twilio_service.send_sms(
                        to_number=function_args["to_number"],
                        message=function_args["message"]
                    )
                    
                    # Add function result to conversation (result is always a dict)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                    
                    if result.get("status") in ["success", "pending"]:
                        logger.info(f"SMS sent successfully: {result.get('message_sid', 'unknown')}, Twilio status: {result.get('twilio_status', 'unknown')}")
                    else:
                        logger.warning(f"SMS send failed: {result.get('error', 'unknown error')}")
            
            # Get final response from AI after function execution
            final_response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                tools=[{"type": "function", "function": func["function"]} for func in functions],
                tool_choice="auto"
            )
            
            final_message = final_response.choices[0].message
            ai_response = final_message.content
            
            # If AI wants to call another function, handle it (up to 2 iterations to avoid loops)
            if final_message.tool_calls:
                logger.info("AI requested additional function calls after SMS attempt")
                # For now, just use the content if available, or provide a helpful message
                if not ai_response:
                    ai_response = "I attempted to send the message, but encountered an issue. Please check the error details above."
        
        logger.info(f"Guest chat response: {len(ai_response) if ai_response else 0} characters")
        
        return JSONResponse({
            "response": ai_response or "I've processed your request.",
            "widgets": None,
            "widget_data": None
        })
        
    except Exception as e:
        logger.error(f"Error in guest chat: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

