"""
Guest-friendly chat endpoint for dashboard.
Allows users to chat with AI assistant without requiring authentication.
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
import re
from openai import OpenAI
from app.core.config import get_settings
from app.services.integration.twilio_service import get_twilio_service
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)

router = APIRouter()

def _extract_workout_data(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Extract structured workout data from AI response text.
    Returns a dict with workout plan information if found.
    Handles multiple formats: numbered lists, bullet points, bold text, plain text.
    """
    if not response_text:
        return None
    
    workout_data = {
        "exercises": [],
        "plan_name": "Workout Plan",
        "description": ""
    }
    
    # Try to extract exercises from numbered lists or bullet points
    lines = response_text.split('\n')
    current_exercise = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Pattern 1: Numbered list with bold (e.g., "1. **Push-ups**: 3 sets of 10")
        numbered_bold_match = re.match(r'^\d+\.\s*\*\*(.*?)\*\*', line)
        if numbered_bold_match:
            exercise_name = numbered_bold_match.group(1).strip()
            if current_exercise:
                workout_data["exercises"].append(current_exercise)
            current_exercise = {
                "name": exercise_name,
                "sets": None,
                "reps": None,
                "description": ""
            }
            # Remove the numbered prefix and bold markers
            line = re.sub(r'^\d+\.\s*\*\*.*?\*\*:?\s*', '', line)
        
        # Pattern 2: Numbered list without bold (e.g., "1. Push-ups: 3 sets of 10")
        elif re.match(r'^\d+\.\s+[A-Z]', line):
            numbered_match = re.match(r'^\d+\.\s+(.+?)(?::|$)', line)
            if numbered_match:
                exercise_name = numbered_match.group(1).strip()
                # Remove common prefixes
                exercise_name = re.sub(r'^\*\*|\*\*$', '', exercise_name).strip()
                if current_exercise:
                    workout_data["exercises"].append(current_exercise)
                current_exercise = {
                    "name": exercise_name,
                    "sets": None,
                    "reps": None,
                    "description": ""
                }
                line = re.sub(r'^\d+\.\s+.*?:?\s*', '', line)
        
        # Pattern 3: Bold text (without numbers) (e.g., "**Push-ups**: 3 sets of 10")
        elif '**' in line and not current_exercise:
            bold_text = re.findall(r'\*\*(.*?)\*\*', line)
            if bold_text:
                exercise_name = bold_text[0].strip()
                if current_exercise:
                    workout_data["exercises"].append(current_exercise)
                current_exercise = {
                    "name": exercise_name,
                    "sets": None,
                    "reps": None,
                    "description": ""
                }
                line = re.sub(r'\*\*.*?\*\*:?\s*', '', line)
        
        # Pattern 4: Lines starting with exercise-like text (e.g., "Push-ups: 3 sets of 10")
        elif not current_exercise and re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+Press|Push|Pull|Squat|Lift|Curl|Extension|Raise|Fly|Row|Press|Dip|Extension):', line):
            exercise_match = re.match(r'^(.+?):', line)
            if exercise_match:
                exercise_name = exercise_match.group(1).strip()
                current_exercise = {
                    "name": exercise_name,
                    "sets": None,
                    "reps": None,
                    "description": ""
                }
                line = re.sub(r'^.+?:\s*', '', line)
        
        # Extract sets/reps from current line (multiple patterns)
        if current_exercise:
            # Pattern: "3 sets of 10 reps" or "3x10" or "3 sets x 10 reps"
            sets_reps_match = re.search(r'(\d+)\s*(?:sets?\s*(?:of\s*|x\s*)?|x\s*)(\d+)\s*(?:reps?|times?)?', line, re.IGNORECASE)
            if sets_reps_match:
                current_exercise["sets"] = int(sets_reps_match.group(1))
                current_exercise["reps"] = int(sets_reps_match.group(2))
            
            # Pattern: "10 reps x 3 sets"
            reps_sets_match = re.search(r'(\d+)\s*reps?\s*(?:x|×)\s*(\d+)\s*sets?', line, re.IGNORECASE)
            if reps_sets_match:
                current_exercise["reps"] = int(reps_sets_match.group(1))
                current_exercise["sets"] = int(reps_sets_match.group(2))
            
            # Add description if it's not an exercise name and contains useful info
            if not re.match(r'^\d+\.\s*\*\*', line) and not '**' in line and not sets_reps_match and not reps_sets_match:
                # Skip lines that are just dashes, bullets, or common workout section headers
                skip_patterns = ['warm', 'cool', 'rest', 'notes', 'tips', 'instructions', '---', '===']
                if line and not line.startswith('-') and not line.startswith('•') and not any(pattern in line.lower() for pattern in skip_patterns):
                    if current_exercise["description"]:
                        current_exercise["description"] += " " + line
                    else:
                        current_exercise["description"] = line
    
    # Add last exercise if exists
    if current_exercise:
        workout_data["exercises"].append(current_exercise)
    
    # If we found exercises, return the data
    if workout_data["exercises"]:
        return workout_data
    
    return None

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
        
        # Add comprehensive system prompt for Physical Education assistant with all capabilities
        # Enhanced system prompt with detailed widget descriptions for better AI understanding
        from app.core.ai_system_prompts import ENHANCED_SYSTEM_PROMPT
        system_prompt = ENHANCED_SYSTEM_PROMPT
        
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
        
        # Add conversation context if provided (limit to prevent token overflow)
        # Truncate long messages to keep within token limits
        if request.context:
            for ctx in request.context[:2]:  # Limit to 2 context messages max
                if isinstance(ctx, dict) and 'role' in ctx and 'content' in ctx:
                    content = ctx['content']
                    # Truncate very long messages to prevent token overflow
                    if len(content) > 500:
                        content = content[:500] + "..."
                    messages.append({
                        "role": ctx['role'],
                        "content": content
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
        
        # Detect if response is about workout/fitness and extract structured data
        widget_data = None
        message_lower = request.message.lower()
        response_lower = (ai_response or "").lower()
        
        # Check if this is a workout/fitness related request (expanded keywords)
        fitness_keywords = ["workout", "exercise", "fitness", "chest", "training", "routine", "plan", "muscle", "strength", "cardio", "gym"]
        is_fitness_request = any(keyword in message_lower for keyword in fitness_keywords) or any(keyword in response_lower for keyword in ["exercise", "workout", "sets", "reps", "push", "pull", "squat", "bench"])
        
        if is_fitness_request:
            logger.info(f"Detected workout/fitness request (message: '{request.message[:50]}...'), extracting data from response")
            logger.info(f"Response preview: {ai_response[:200] if ai_response else 'None'}...")
            # Try to extract workout plan data from the response
            workout_data = _extract_workout_data(ai_response or "")
            logger.info(f"Extracted workout data: {workout_data}")
            if workout_data and workout_data.get("exercises") and len(workout_data["exercises"]) > 0:
                widget_data = {
                    "type": "fitness",
                    "data": workout_data
                }
                logger.info(f"✅ Created widget_data with {len(workout_data['exercises'])} exercises: {widget_data}")
            else:
                logger.warning(f"⚠️ Failed to extract workout data - workout_data: {workout_data}, exercises: {workout_data.get('exercises') if workout_data else None}")
        else:
            logger.info(f"Not a fitness request - message: '{request.message[:50]}...'")
        
        logger.info(f"Returning response with widget_data: {widget_data is not None}")
        return JSONResponse({
            "response": ai_response or "I've processed your request.",
            "widgets": None,
            "widget_data": widget_data
        })
        
    except Exception as e:
        logger.error(f"Error in guest chat: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

