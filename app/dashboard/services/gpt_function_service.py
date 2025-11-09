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
        
        # Call OpenAI with the command and available tools
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "You are an AI dashboard assistant for Physical Education, Health, and Drivers Ed. Use the available tools to help the user control widgets and manage their classes. You can create teams, track attendance, predict performance, and more."},
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