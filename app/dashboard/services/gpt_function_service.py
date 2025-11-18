from typing import Dict, Any, Optional
import openai
import json
import logging
from sqlalchemy.orm import Session
from app.dashboard.services.tool_registry_service import ToolRegistryService
from app.dashboard.services.gpt_coordination_service import GPTCoordinationService
from app.dashboard.services.ai_widget_service import AIWidgetService
from app.dashboard.services.widget_function_schemas import WidgetFunctionSchemas

logger = logging.getLogger(__name__)

class GPTFunctionService:
    def __init__(self, db: Session, user_id: Optional[str] = None):
        self.db = db
        self.user_id = user_id
        self.tool_registry = ToolRegistryService(db)
        self.gpt_coordinator = GPTCoordinationService(db)
        self.ai_widget_service = AIWidgetService(db, user_id=int(user_id) if user_id and isinstance(user_id, str) and user_id.isdigit() else user_id)

    async def process_user_command(self, user_id: str, command: str) -> Dict[str, Any]:
        # Get available tool schemas for the user
        tool_schemas = self.tool_registry.get_tool_function_schemas(user_id)
        
        # Add widget function schemas
        widget_schemas = WidgetFunctionSchemas.get_all_schemas()
        
        # Combine all schemas
        all_schemas = tool_schemas + widget_schemas
        
        # Get GPT context for the user
        context = await self.gpt_coordinator.get_user_context(user_id)
        
        # Comprehensive system prompt (same as guest_chat.py and ai_assistant_service.py)
        comprehensive_system_prompt = """You are an advanced AI assistant for Physical Education teachers with access to 39 comprehensive widgets that control every aspect of PE instruction, plus extensive communication, integration, and analysis capabilities. You are a powerful natural language interface that allows teachers to control and interact with all features through conversational commands.

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

Use the available tools and functions to help the user control widgets and manage their classes. You can create teams, track attendance, predict performance, send emails and SMS with translation, and much more."""

        # Call OpenAI with the command and available tools
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": comprehensive_system_prompt},
                {"role": "user", "content": command}
            ],
            functions=all_schemas,
            function_call="auto"
        )
        
        # Process the response
        message = response.choices[0].message
        
        if message.function_call:
            # Execute the function call
            function_name = message.function_call.name
            function_args = json.loads(message.function_call.arguments) if isinstance(message.function_call.arguments, str) else message.function_call.arguments
            
            # Route to the appropriate tool
            result = await self._execute_function_call(function_name, function_args, user_id)
            
            # Get a natural language response about the result
            follow_up = await openai.ChatCompletion.acreate(
                model="gpt-4-0613",
                messages=[
                    {"role": "system", "content": "You are an AI dashboard assistant. Explain the result of the tool execution in a friendly, helpful way."},
                    {"role": "user", "content": f"Tool {function_name} returned: {json.dumps(result)}"}
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

    async def _execute_function_call(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        user_id: str
    ) -> Any:
        """
        Execute a function call by routing to the appropriate service.
        
        This routes widget function calls to the AI widget service.
        """
        try:
            # Route widget functions to AI widget service
            if function_name == "get_attendance_patterns":
                return await self.ai_widget_service.predict_attendance_patterns(
                    class_id=arguments.get("class_id"),
                    student_id=arguments.get("student_id"),
                    days_ahead=arguments.get("days_ahead", 7)
                )
            
            elif function_name == "create_teams":
                team_config = arguments.get("team_config", {})
                return await self.ai_widget_service.suggest_team_configurations(
                    class_id=arguments.get("class_id"),
                    activity_type=arguments.get("activity_type", "general"),
                    team_count=team_config.get("team_count", 2),
                    squad_count=team_config.get("squad_count", 0),
                    period=arguments.get("period"),
                    teacher_id=arguments.get("teacher_id"),
                    team_config=team_config
                )
            
            elif function_name == "suggest_adaptive_accommodations":
                return await self.ai_widget_service.suggest_adaptive_accommodations(
                    student_id=arguments.get("student_id"),
                    activity_type=arguments.get("activity_type"),
                    medical_notes=arguments.get("medical_notes")
                )
            
            elif function_name == "predict_student_performance":
                return await self.ai_widget_service.predict_student_performance(
                    student_id=arguments.get("student_id"),
                    activity_id=arguments.get("activity_id"),
                    weeks_ahead=arguments.get("weeks_ahead", 4)
                )
            
            elif function_name == "identify_safety_risks":
                return await self.ai_widget_service.identify_safety_risks(
                    class_id=arguments.get("class_id"),
                    activity_id=arguments.get("activity_id")
                )
            
            elif function_name == "get_class_insights":
                return await self.ai_widget_service.generate_comprehensive_insights(
                    class_id=arguments.get("class_id"),
                    include_attendance=arguments.get("include_attendance", True),
                    include_performance=arguments.get("include_performance", True),
                    include_health=arguments.get("include_health", True)
                )
            
            # Health Widget Functions
            elif function_name == "analyze_health_trends":
                return await self.ai_widget_service.analyze_health_trends(
                    student_id=arguments.get("student_id"),
                    class_id=arguments.get("class_id"),
                    metric_type=arguments.get("metric_type"),
                    time_range=arguments.get("time_range", "month")
                )
            elif function_name == "identify_health_risks":
                return await self.ai_widget_service.identify_health_risks(
                    class_id=arguments.get("class_id"),
                    student_id=arguments.get("student_id"),
                    risk_threshold=arguments.get("risk_threshold", "medium")
                )
            elif function_name == "generate_health_recommendations":
                return await self.ai_widget_service.generate_health_recommendations(
                    student_id=arguments.get("student_id"),
                    focus_area=arguments.get("focus_area", "general")
                )
            
            # Drivers Ed Widget Functions
            elif function_name == "create_drivers_ed_lesson_plan":
                # Get teacher_id from current user context if available
                teacher_id = arguments.get("teacher_id")
                if not teacher_id and hasattr(self, 'current_user_id'):
                    # Try to get teacher_id from user context
                    # This would need to be passed in process_user_command
                    pass
                
                return await self.ai_widget_service.create_drivers_ed_lesson_plan(
                    title=arguments.get("title"),
                    topic=arguments.get("topic"),
                    objectives=arguments.get("objectives"),
                    activities=arguments.get("activities"),
                    standards=arguments.get("standards"),
                    teacher_id=teacher_id,
                    class_id=arguments.get("class_id")
                )
            elif function_name == "track_student_driving_progress":
                return await self.ai_widget_service.track_student_driving_progress(
                    student_id=arguments.get("student_id"),
                    driving_hours=arguments.get("driving_hours"),
                    skill_assessment=arguments.get("skill_assessment"),
                    test_score=arguments.get("test_score")
                )
            elif function_name == "record_safety_incident":
                return await self.ai_widget_service.record_safety_incident(
                    class_id=arguments.get("class_id"),
                    incident_type=arguments.get("incident_type"),
                    description=arguments.get("description"),
                    student_id=arguments.get("student_id"),
                    date=arguments.get("date"),
                    severity=arguments.get("severity"),
                    activity_id=arguments.get("activity_id"),
                    teacher_id=arguments.get("teacher_id")
                )
            elif function_name == "manage_vehicle":
                return await self.ai_widget_service.manage_vehicle(
                    action=arguments.get("action"),
                    vehicle_id=arguments.get("vehicle_id"),
                    vehicle_data=arguments.get("vehicle_data"),
                    maintenance_type=arguments.get("maintenance_type"),
                    maintenance_date=arguments.get("maintenance_date")
                )
            
            # Additional PE Widget Functions
            elif function_name == "mark_attendance":
                return await self.ai_widget_service.mark_attendance(
                    class_id=arguments.get("class_id"),
                    attendance_records=arguments.get("attendance_records"),
                    date=arguments.get("date")
                )
            elif function_name == "get_class_roster":
                # Support period-based lookup if class_id not provided
                class_id = arguments.get("class_id")
                period = arguments.get("period")
                teacher_id = arguments.get("teacher_id")
                
                # If period provided but no class_id, find class by period
                if period and not class_id:
                    pe_class = self.ai_widget_service._find_class_by_period(period, teacher_id)
                    if pe_class:
                        class_id = pe_class.id
                
                return await self.ai_widget_service.get_class_roster(
                    class_id=class_id,
                    period=period,
                    teacher_id=teacher_id
                )
            elif function_name == "create_adaptive_activity":
                return await self.ai_widget_service.create_adaptive_activity(
                    student_id=arguments.get("student_id"),
                    activity_name=arguments.get("activity_name"),
                    base_activity_id=arguments.get("base_activity_id"),
                    modifications=arguments.get("modifications"),
                    equipment=arguments.get("equipment"),
                    safety_notes=arguments.get("safety_notes"),
                    difficulty_level=arguments.get("difficulty_level")
                )
            
            # Enhancement Functions
            elif function_name == "predict_student_performance_advanced":
                return await self.ai_widget_service.predict_student_performance_advanced(
                    student_id=arguments.get("student_id"),
                    activity_id=arguments.get("activity_id"),
                    weeks_ahead=arguments.get("weeks_ahead", 4),
                    include_health_factors=arguments.get("include_health_factors", True),
                    include_attendance_factors=arguments.get("include_attendance_factors", True)
                )
            elif function_name == "generate_automated_report":
                return await self.ai_widget_service.generate_automated_report(
                    report_type=arguments.get("report_type"),
                    student_id=arguments.get("student_id"),
                    class_id=arguments.get("class_id"),
                    time_range=arguments.get("time_range", "month"),
                    format=arguments.get("format", "text")
                )
            elif function_name == "send_automated_notification":
                return await self.ai_widget_service.send_automated_notification(
                    notification_type=arguments.get("notification_type"),
                    recipient_id=arguments.get("recipient_id"),
                    recipient_type=arguments.get("recipient_type", "student"),
                    message=arguments.get("message"),
                    channel=arguments.get("channel", "email")
                )
            elif function_name == "execute_workflow":
                return await self.ai_widget_service.execute_workflow(
                    workflow_name=arguments.get("workflow_name"),
                    class_id=arguments.get("class_id"),
                    parameters=arguments.get("parameters", {})
                )
            elif function_name == "analyze_cross_widget_correlations":
                return await self.ai_widget_service.analyze_cross_widget_correlations(
                    class_id=arguments.get("class_id"),
                    student_id=arguments.get("student_id"),
                    time_range=arguments.get("time_range", "month")
                )
            elif function_name == "detect_anomalies":
                return await self.ai_widget_service.detect_anomalies(
                    class_id=arguments.get("class_id"),
                    student_id=arguments.get("student_id"),
                    data_type=arguments.get("data_type", "performance")
                )
            elif function_name == "create_smart_alert":
                return await self.ai_widget_service.create_smart_alert(
                    alert_type=arguments.get("alert_type"),
                    student_id=arguments.get("student_id"),
                    class_id=arguments.get("class_id"),
                    threshold=arguments.get("threshold"),
                    conditions=arguments.get("conditions")
                )
            elif function_name == "get_student_dashboard_data":
                return await self.ai_widget_service.get_student_dashboard_data(
                    student_id=arguments.get("student_id"),
                    include_goals=arguments.get("include_goals", True),
                    include_progress=arguments.get("include_progress", True)
                )
            elif function_name == "create_student_self_assessment":
                return await self.ai_widget_service.create_student_self_assessment(
                    student_id=arguments.get("student_id"),
                    assessment_data=arguments.get("assessment_data", {})
                )
            elif function_name == "predict_equipment_failure":
                return await self.ai_widget_service.predict_equipment_failure(
                    equipment_id=arguments.get("equipment_id"),
                    equipment_name=arguments.get("equipment_name"),
                    time_horizon=arguments.get("time_horizon", 30)
                )
            elif function_name == "optimize_equipment_inventory":
                return await self.ai_widget_service.optimize_equipment_inventory(
                    class_id=arguments.get("class_id"),
                    activity_type=arguments.get("activity_type")
                )
            
            # Communication Functions with Translation
            elif function_name == "send_parent_message":
                return await self.ai_widget_service.send_parent_message(
                    student_id=arguments.get("student_id"),
                    message=arguments.get("message"),
                    message_type=arguments.get("message_type", "progress_update"),
                    channels=arguments.get("channels", ["email"]),
                    target_language=arguments.get("target_language"),
                    auto_translate=arguments.get("auto_translate", True)
                )
            elif function_name == "send_student_message":
                return await self.ai_widget_service.send_student_message(
                    student_id=arguments.get("student_id"),
                    message=arguments.get("message"),
                    channels=arguments.get("channels", ["email"]),
                    target_language=arguments.get("target_language"),
                    auto_translate=arguments.get("auto_translate", True)
                )
            elif function_name == "send_teacher_message":
                return await self.ai_widget_service.send_teacher_message(
                    recipient_teacher_id=arguments.get("recipient_teacher_id"),
                    message=arguments.get("message"),
                    channels=arguments.get("channels", ["email"]),
                    target_language=arguments.get("target_language")
                )
            elif function_name == "send_administrator_message":
                return await self.ai_widget_service.send_administrator_message(
                    message=arguments.get("message"),
                    admin_emails=arguments.get("admin_emails"),
                    channels=arguments.get("channels", ["email"])
                )
            elif function_name == "send_assignment_to_students":
                return await self.ai_widget_service.send_assignment_to_students(
                    assignment_id=arguments.get("assignment_id"),
                    student_ids=arguments.get("student_ids"),
                    target_languages=arguments.get("target_languages"),
                    channels=arguments.get("channels", ["email"])
                )
            elif function_name == "translate_assignment_submission":
                return await self.ai_widget_service.translate_assignment_submission(
                    submission_text=arguments.get("submission_text"),
                    target_language=arguments.get("target_language", "en"),
                    source_language=arguments.get("source_language")
                )
            elif function_name == "generate_parent_message":
                return await self.ai_widget_service.generate_parent_message(
                    student_id=arguments.get("student_id"),
                    message_type=arguments.get("message_type"),
                    key_points=arguments.get("key_points"),
                    tone=arguments.get("tone", "professional")
                )
            
            # For now, return a placeholder for unhandled functions
            else:
                logger.warning(f"Unhandled function call: {function_name}")
                return {
                    "error": f"Function {function_name} not yet implemented",
                    "arguments": arguments,
                    "note": "This function may need additional implementation in ai_widget_service.py"
                }
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {str(e)}")
            raise

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