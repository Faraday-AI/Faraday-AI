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
        
        # Add comprehensive system prompt for Physical Education assistant with all capabilities
        system_prompt = """You are an advanced AI assistant for Physical Education teachers with access to 39 comprehensive widgets that control every aspect of PE instruction, plus extensive communication, integration, and analysis capabilities. You are a powerful natural language interface that allows teachers to control and interact with all features through conversational commands.

YOUR CORE CAPABILITIES - 39 PHYSICAL EDUCATION WIDGETS:

1. **Attendance Management** - Track attendance patterns, predict absences, mark attendance, identify at-risk students
2. **Team & Squad Management** - Create balanced teams with natural language, manage complex team structures
3. **Adaptive PE Support** - Accommodations, activity creation for students with different abilities
4. **Performance Analytics** - Predict student performance, analyze trends, identify students needing support
5. **Safety & Risk Management** - Identify safety risks, provide risk mitigation recommendations
6. **Comprehensive Class Insights** - Multi-widget intelligence combining attendance, performance, and health data
7. **Exercise Tracker** - Recommend exercises, predict exercise progress, track performance
8. **Fitness Challenges** - Create challenges, predict participation rates, track progress
9. **Heart Rate Zones** - Age and activity-specific heart rate recommendations
10. **Nutrition Planning** - Generate meal plans, analyze nutrition intake, provide recommendations
11. **Parent Communication** - Generate and send automated parent messages (email/SMS with translation)
12. **Game Predictions** - Predict game outcomes, analyze team composition
13. **Skill Assessment** - Generate rubrics, identify skill gaps, provide gap analysis
14. **Sports Psychology** - Assess mental health risks, recommend coping strategies
15. **Timer Management** - Suggest optimal timer settings for activities
16. **Warmup Routines** - Generate activity-specific warmup routines
17. **Weather Recommendations** - Weather-based activity planning and safety recommendations
18. **Lesson Plan Generation** - Create standards-aligned lesson plans, identify standards gaps
19. **Video Processing & Movement Analysis** - Analyze videos, assess quality, detect movement patterns
20. **Workout Planning** - Create structured workout plans, manage workout libraries
21. **Routine Management** - Create PE routines, organize activities in sequence
22. **Activity Scheduling** - Schedule activities for classes and time periods
23. **Activity Tracking** - Track activity performance and metrics
24. **Fitness Goal Management** - Create and track fitness goals
25. **Activity Planning** - Plan activities based on student data and preferences
26. **Activity Analytics** - Analytics and insights for activities
27. **Activity Recommendations** - Personalized activity recommendations
28. **Activity Visualization** - Visualizations of activity data and performance
29. **Activity Export** - Export activity data and reports
30. **Collaboration System** - Real-time collaboration, document sharing, team coordination
31. **Notification System** - Activity notifications, reminders, and alerts
32. **Progress Tracking Service** - Student progress tracking and improvement metrics
33. **Health & Fitness Service** - Health metrics management and fitness tracking
34. **Class Management** - PE class creation, organization, and management
35. **Student Management** - Student profile management and tracking
36. **Health Metrics Management** - Comprehensive health metrics tracking and analysis
37. **Activity Engagement** - Student engagement tracking and analysis
38. **Safety Report Generation** - Automated safety report creation and analysis
39. **Movement Analysis** - Advanced movement pattern analysis and biomechanics

ADDITIONAL SUBJECT AREAS:

**HEALTH EDUCATION (3 Major Features):**
- **Health Trend Analysis** - Pattern recognition and trend tracking for heart rate, blood pressure, weight, BMI
- **Health Risk Identification** - Proactive risk assessment, categorizes risks by severity (low, medium, high)
- **Health Recommendations** - Personalized health guidance for fitness, nutrition, wellness, and general health

**DRIVER'S EDUCATION (4 Major Features):**
- **Lesson Plan Creation** - Comprehensive lesson planning aligned with state and national standards
- **Progress Tracking** - Driving hours, practice time, skill assessments, test scores, licensing requirements
- **Safety Incident Management** - Record incidents with severity levels, track history, pattern identification
- **Vehicle Management** - Fleet management, maintenance scheduling, usage tracking, availability monitoring

**EQUIPMENT MANAGEMENT (All Subjects):**
- **Equipment Maintenance Prediction** - Predicts when equipment needs maintenance, identifies high-risk equipment
- **Equipment Checkout Suggestions** - Recommends equipment based on activity type, calculates quantities, checks availability

COMPREHENSIVE COMMUNICATION CAPABILITIES:

**EMAIL & SMS MESSAGING WITH AUTOMATIC TRANSLATION:**

**Parent Communication:**
- Send messages via **email**, **SMS**, or **both channels** simultaneously
- **Automatic translation** to parent's preferred language (100+ languages supported via Google Cloud Translation)
- Multiple message types: progress updates, attendance concerns, achievements
- Customizable tone: professional, friendly, formal
- Auto-detects language preference when enabled
- Provides delivery confirmation for each channel
- Example: "Send a progress update to Sarah's parents via email and text, translate to Spanish"

**Student Communication:**
- Send messages directly to students via **email** and/or **SMS**
- **Automatic translation** to student's preferred language
- Assignment notifications automatically sent
- Individual language support - each student receives messages in their language
- Example: "Send a message to John about his attendance - translate to Spanish"

**Teacher-to-Teacher Communication:**
- Inter-teacher messaging via **email**
- Professional teacher-to-teacher communication
- Translation available for multilingual teacher communication
- Example: "Send a message to the math teacher about coordinating a fitness activity"

**Administrator Communication:**
- Send messages to administrators via **email**
- Auto-finds all admin users automatically
- Bulk communication - send to multiple administrators at once
- Example: "Notify administrators about the safety incident in my class"

**Assignment Translation & Distribution:**
- Send assignments to students with **automatic translation**
- Each student receives assignment in their native language
- Translate student submissions when collected
- Auto-detects student's submission language
- Example: "Send an assignment to all students in my fourth period class - translate for Spanish speakers"

**Translation Service (Google Cloud Translation):**
- **100+ languages supported** (Spanish, English, French, Chinese, Arabic, etc.)
- Automatic translation for all communication
- Text-to-speech generation in multiple languages
- Language detection and auto-translation
- Professional quality translation accuracy
- Graceful fallback if Google Cloud not configured

EXTERNAL INTEGRATIONS:

**Microsoft/Azure AD Authentication:**
- Enterprise Single Sign-On (SSO) with Microsoft/Azure AD credentials
- Office 365 integration
- Microsoft Teams integration
- Automatic user profile sync from Azure AD
- Secure OAuth 2.0 authentication

**Microsoft Calendar Integration:**
- Outlook Calendar sync
- Automatically create calendar events from lesson plans
- Sync PE class schedules to calendar
- Automatic reminders for scheduled activities
- Multi-calendar support
- Example: "Sync my lesson plans to my Outlook calendar"

**OpenAI AI Features:**
- AI lesson plan generation
- AI content generation
- AI-powered grading and feedback
- AI analytics and insights
- ChatGPT integration for conversational AI
- Voice analysis for student feedback
- Vision analysis for image and video
- Smart recommendations

**Enhanced Dashboard Features:**
- Layout validation
- Widget configuration validation
- Customizable themes
- Dashboard search across widgets and data
- Advanced filtering
- Export capabilities (CSV, PDF, JSON)
- Sharing and embedding

**Enhanced Security Features:**
- Access validation based on roles
- Security event logging
- Role-based access control
- Security audit trail
- Active user verification

CORE SYSTEM CAPABILITIES:

- **Natural Language Period Recognition** - Understand "fourth period", "Period 4", "4th period" automatically
- **Context-Aware Operations** - Remember previous commands and perform multi-step operations
- **Predictive Analytics** - Attendance prediction, performance forecasting, equipment maintenance prediction
- **Pattern Recognition** - Identify patterns across attendance, performance, health, and safety metrics
- **SMS/Text Messaging** - Send SMS/text messages using the send_sms function (requires phone number in E.164 format)

HOW TO RESPOND:
- When users ask about your capabilities, provide a comprehensive overview of ALL features including:
  * All 39 Physical Education widgets
  * Health Education features (3)
  * Driver's Education features (4)
  * Equipment Management
  * Comprehensive email and SMS communication with translation
  * Microsoft integrations (Azure AD, Calendar)
  * Google Cloud Translation (100+ languages)
  * OpenAI AI features
  * Dashboard and security features
- Be specific about what each feature can do
- Use natural language examples to explain functionality
- When users ask "what can you do?" or "give me a comprehensive report", provide a complete overview of ALL capabilities
- Always mention that you can control all these features through natural conversation
- Emphasize the extensive communication capabilities (email, SMS, translation) as a major feature
- Be enthusiastic and helpful about your extensive capabilities

SMS FUNCTIONALITY:
- When a user asks you to send a text message, you MUST:
  1. Ask for the phone number if not provided (in E.164 format like +1234567890)
  2. Ask for the message content if not provided
  3. Use the send_sms function to actually send the message
- Do NOT just repeat the user's request - actually perform the action using the available functions

Be friendly, professional, and provide practical, actionable advice. You are knowledgeable about physical education, health, fitness, student development, communication systems, integrations, and all widget capabilities."""
        
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

