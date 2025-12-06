from typing import Dict, Any, Optional
import openai
import json
import logging
import base64
import os
from sqlalchemy.orm import Session
from app.dashboard.services.tool_registry_service import ToolRegistryService
from app.dashboard.services.gpt_coordination_service import GPTCoordinationService
from app.dashboard.services.ai_widget_service import AIWidgetService
from app.dashboard.services.widget_function_schemas import WidgetFunctionSchemas
from app.models.core.user import User
from app.models.teacher_registration import TeacherRegistration
from app.services.integration.msgraph_service import get_msgraph_service
from app.models.integration.microsoft_token import MicrosoftOAuthToken
from app.services.integration.token_encryption import get_token_encryption_service
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GPTFunctionService:
    def __init__(
        self, 
        db: Session, 
        user_id: Optional[str] = None,
        current_user: Optional[User] = None,
        current_teacher: Optional[TeacherRegistration] = None
    ):
        self.db = db
        self.user_id = user_id
        self.current_user = current_user
        self.current_teacher = current_teacher
        self.tool_registry = ToolRegistryService(db)
        self.gpt_coordinator = GPTCoordinationService(db)
        
        # Convert user_id to int if needed
        user_id_int = None
        if user_id:
            if isinstance(user_id, str) and user_id.isdigit():
                user_id_int = int(user_id)
            elif isinstance(user_id, int):
                user_id_int = user_id
        
        # Initialize AIWidgetService with admin context
        self.ai_widget_service = AIWidgetService(
            db, 
            user_id=user_id_int,
            current_user=current_user,
            current_teacher=current_teacher
        )

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
        # Enhanced system prompt with detailed widget descriptions for better AI understanding
        from app.core.ai_system_prompts import ENHANCED_SYSTEM_PROMPT
        comprehensive_system_prompt = ENHANCED_SYSTEM_PROMPT

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
            
            # Extract content from function result for frontend display
            response_data = {
                "action": function_name,
                "result": result,
                "response": follow_up.choices[0].message.content,
                "explanation": follow_up.choices[0].message.content
            }
            
            # Extract images, file_content, web_url, widget_data from result
            if isinstance(result, dict):
                if result.get("images"):
                    response_data["images"] = result.get("images", [])
                if result.get("file_content"):
                    response_data["file_content"] = result.get("file_content")
                    response_data["filename"] = result.get("filename")
                if result.get("web_url"):
                    response_data["web_url"] = result.get("web_url")
                    response_data["file_id"] = result.get("file_id")
                    if result.get("filename"):
                        response_data["filename"] = result.get("filename")
                if result.get("widget_data"):
                    response_data["widget_data"] = result.get("widget_data")
                # Also include num_slides and other metadata
                if result.get("num_slides"):
                    response_data["num_slides"] = result.get("num_slides")
            
            return response_data
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
                    period=arguments.get("period"),
                    student_id=arguments.get("student_id"),
                    days_ahead=arguments.get("days_ahead", 7),
                    teacher_id=arguments.get("teacher_id"),
                    teacher_name=arguments.get("teacher_name"),
                    teacher_email=arguments.get("teacher_email")
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
                    period=arguments.get("period"),
                    attendance_records=arguments.get("attendance_records"),
                    date=arguments.get("date"),
                    teacher_id=arguments.get("teacher_id"),
                    teacher_name=arguments.get("teacher_name"),
                    teacher_email=arguments.get("teacher_email")
                )
            elif function_name == "get_class_roster":
                return await self.ai_widget_service.get_class_roster(
                    class_id=arguments.get("class_id"),
                    period=arguments.get("period"),
                    teacher_id=arguments.get("teacher_id"),
                    teacher_name=arguments.get("teacher_name"),
                    teacher_email=arguments.get("teacher_email")
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
            elif function_name == "send_sms":
                # Direct SMS sending for testing
                from app.services.integration.twilio_service import get_twilio_service
                twilio_service = get_twilio_service()
                phone_number = arguments.get("phone_number")
                message = arguments.get("message")
                
                if not phone_number or not message:
                    return {
                        "status": "error",
                        "message": "Phone number and message are required"
                    }
                
                try:
                    sms_result = await twilio_service.send_sms(
                        to_number=phone_number,
                        message=message
                    )
                    if sms_result.get("status") in ["success", "pending"]:
                        return {
                            "status": "success",
                            "message": sms_result.get("message", "SMS sent successfully"),
                            "message_sid": sms_result.get("message_sid"),
                            "twilio_status": sms_result.get("twilio_status"),
                            "to": sms_result.get("to")
                        }
                    else:
                        # Error case - pass through error details
                        return {
                            "status": "error",
                            "error": sms_result.get("error", sms_result.get("message", "Unknown error")),
                            "details": sms_result.get("details", ""),
                            "to": sms_result.get("to", phone_number)
                        }
                except Exception as e:
                    logger.error(f"Error sending SMS: {str(e)}")
                    return {
                        "status": "error",
                        "error": f"Failed to send SMS: {str(e)}",
                        "to": phone_number
                    }
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
            
            # Document Creation Functions
            elif function_name == "create_powerpoint_presentation":
                return await self._handle_create_powerpoint_presentation(user_id, arguments)
            elif function_name == "create_word_document":
                return await self._handle_create_word_document(user_id, arguments)
            elif function_name == "create_pdf_document":
                return await self._handle_create_pdf_document(user_id, arguments)
            elif function_name == "create_excel_spreadsheet":
                return await self._handle_create_excel_spreadsheet(user_id, arguments)
            
            # Media Creation Functions
            elif function_name == "generate_image":
                return await self._handle_generate_image(user_id, arguments)
            elif function_name == "search_and_embed_video":
                return await self._handle_search_and_embed_video(user_id, arguments)
            elif function_name == "search_and_embed_web_links":
                return await self._handle_search_and_embed_web_links(user_id, arguments)
            
            # Microsoft Graph Functions
            elif function_name == "send_email_via_outlook":
                return await self._handle_send_email_via_outlook(user_id, arguments)
            elif function_name == "upload_to_onedrive":
                return await self._handle_upload_to_onedrive(user_id, arguments)
            elif function_name == "share_onedrive_file":
                return await self._handle_share_onedrive_file(user_id, arguments)
            
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
    
    def _get_microsoft_token(self, user_id: str) -> Optional[str]:
        """Get Microsoft access token for user, refreshing if necessary."""
        try:
            # Convert user_id to int if needed
            user_id_int = None
            if isinstance(user_id, str) and user_id.isdigit():
                user_id_int = int(user_id)
            elif isinstance(user_id, int):
                user_id_int = user_id
            else:
                logger.error(f"Invalid user_id format: {user_id}")
                return None
            
            # Get encryption service for decrypting tokens
            encryption_service = get_token_encryption_service()
            
            # Get stored token from database
            oauth_token = self.db.query(MicrosoftOAuthToken).filter(
                MicrosoftOAuthToken.user_id == user_id_int,
                MicrosoftOAuthToken.is_active == True
            ).first()
            
            if not oauth_token:
                logger.warning(f"No active Microsoft token found for user {user_id_int}")
                return None
            
            # Check if token is expired or will expire soon (within 5 minutes)
            if oauth_token.expires_at and oauth_token.expires_at <= datetime.utcnow() + timedelta(minutes=5):
                # Token expired or expiring soon, try to refresh
                if oauth_token.refresh_token:
                    msgraph_service = get_msgraph_service()
                    refresh_result = msgraph_service.refresh_token(oauth_token.refresh_token)
                    
                    if refresh_result.get("status") == "success":
                        token_data = refresh_result.get("token", {})
                        # Update token in database (would need to implement this)
                        # For now, use the new access token
                        return token_data.get("access_token")
                    else:
                        logger.error(f"Failed to refresh token: {refresh_result.get('error')}")
                        return None
            
            # Decrypt and return access token
            if oauth_token.encrypted_access_token:
                try:
                    access_token = encryption_service.decrypt(oauth_token.encrypted_access_token)
                    return access_token
                except Exception as e:
                    logger.error(f"Error decrypting access token: {str(e)}")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Microsoft token: {str(e)}")
            return None
    
    async def _handle_send_email_via_outlook(self, user_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send_email_via_outlook function call."""
        try:
            # Get Microsoft token
            token = self._get_microsoft_token(user_id)
            if not token:
                return {
                    "status": "error",
                    "error": "Microsoft account not connected. Please connect your Microsoft account first."
                }
            
            msgraph_service = get_msgraph_service()
            
            # Prepare attachments if provided
            attachments = None
            if arguments.get("attachments"):
                attachments = []
                for att in arguments.get("attachments", []):
                    attachments.append({
                        "name": att.get("name"),
                        "contentBytes": att.get("content_bytes"),  # Should already be base64
                        "contentType": att.get("content_type", "application/octet-stream")
                    })
            
            # Send email
            result = msgraph_service.send_email_via_outlook(
                token=token,
                recipients=arguments.get("recipients", []),
                subject=arguments.get("subject", ""),
                body=arguments.get("body", ""),
                body_type=arguments.get("body_type", "Text"),
                attachments=attachments
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending email via Outlook: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_upload_to_onedrive(self, user_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle upload_to_onedrive function call."""
        try:
            # Get Microsoft token
            token = self._get_microsoft_token(user_id)
            if not token:
                return {
                    "status": "error",
                    "error": "Microsoft account not connected. Please connect your Microsoft account first."
                }
            
            # Decode base64 file content
            file_content_b64 = arguments.get("file_content", "")
            try:
                file_bytes = base64.b64decode(file_content_b64)
            except Exception as e:
                return {"status": "error", "error": f"Invalid base64 file content: {str(e)}"}
            
            msgraph_service = get_msgraph_service()
            
            # Upload to OneDrive
            result = msgraph_service.upload_to_onedrive(
                token=token,
                file_bytes=file_bytes,
                filename=arguments.get("filename", "file"),
                folder_path=arguments.get("folder_path", ""),
                conflict_behavior=arguments.get("conflict_behavior", "rename")
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error uploading to OneDrive: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_share_onedrive_file(self, user_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle share_onedrive_file function call."""
        try:
            # Get Microsoft token
            token = self._get_microsoft_token(user_id)
            if not token:
                return {
                    "status": "error",
                    "error": "Microsoft account not connected. Please connect your Microsoft account first."
                }
            
            msgraph_service = get_msgraph_service()
            
            # Share file
            result = msgraph_service.share_document(
                token=token,
                file_id=arguments.get("file_id", ""),
                recipients=arguments.get("recipients", []),
                permissions=arguments.get("permissions", "read"),
                send_notification=arguments.get("send_notification", True)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sharing OneDrive file: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_create_powerpoint_presentation(self, user_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_powerpoint_presentation function call."""
        try:
            from app.services.widget_export_service import WidgetExportService
            import base64
            
            presentation_title = arguments.get("presentation_title", "Presentation")
            topic = arguments.get("topic", "")
            num_slides = arguments.get("num_slides", 10)
            subtitle = arguments.get("subtitle")
            upload_to_onedrive = arguments.get("upload_to_onedrive", False)
            onedrive_folder = arguments.get("onedrive_folder", "")
            
            # Get slide outline if provided, otherwise generate slides
            slide_outline = arguments.get("slide_outline")
            
            if not slide_outline:
                # Generate basic slide structure based on topic
                # In a real implementation, you might want to use AI to generate slide content
                slide_outline = []
                for i in range(1, num_slides + 1):
                    slide_outline.append({
                        "title": f"Slide {i}: {topic}",
                        "content": [f"Key point {i} about {topic}", f"Additional information {i}"],
                        "notes": f"Speaker notes for slide {i}"
                    })
            
            # Create presentation
            export_service = WidgetExportService()
            ppt_bytes = export_service.create_presentation_from_slides(
                presentation_title=presentation_title,
                slides=slide_outline,
                subtitle=subtitle
            )
            
            filename = f"{presentation_title.replace(' ', '_')}.pptx"
            
            # If upload to OneDrive is requested
            if upload_to_onedrive:
                token = self._get_microsoft_token(user_id)
                if not token:
                    return {
                        "status": "error",
                        "error": "Microsoft account not connected. Please connect your Microsoft account to upload to OneDrive."
                    }
                
                msgraph_service = get_msgraph_service()
                upload_result = msgraph_service.upload_to_onedrive(
                    token=token,
                    file_bytes=ppt_bytes,
                    filename=filename,
                    folder_path=onedrive_folder or "",
                    conflict_behavior="rename"
                )
                
                if upload_result.get("status") == "success":
                    # Create widget data for OneDrive-uploaded presentation
                    widget_data = {
                        "type": "generated-document",
                        "title": f"Presentation: {presentation_title}",
                        "data": {
                            "document_type": "powerpoint",
                            "filename": upload_result.get("filename", filename),
                            "title": presentation_title,
                            "num_slides": len(slide_outline) + 1,  # +1 for title slide
                            "web_url": upload_result.get("web_url"),
                            "file_id": upload_result.get("file_id"),
                            "onedrive_uploaded": True,
                            "created_at": datetime.now().isoformat() if hasattr(datetime, 'now') else None
                        }
                    }
                    return {
                        "status": "success",
                        "message": f"PowerPoint presentation '{presentation_title}' created and uploaded to OneDrive",
                        "file_id": upload_result.get("file_id"),
                        "web_url": upload_result.get("web_url"),
                        "filename": upload_result.get("filename"),
                        "num_slides": len(slide_outline) + 1,  # +1 for title slide
                        "widget_data": widget_data
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Failed to upload to OneDrive: {upload_result.get('error')}"
                    }
            
            # Return presentation as base64 for download
            ppt_base64 = base64.b64encode(ppt_bytes).decode('utf-8')
            
            # Create widget data for generated presentation
            widget_data = {
                "type": "generated-document",
                "title": f"Presentation: {presentation_title}",
                "data": {
                    "document_type": "powerpoint",
                    "filename": filename,
                    "title": presentation_title,
                    "num_slides": len(slide_outline) + 1,  # +1 for title slide
                    "file_content": ppt_base64,
                    "created_at": datetime.now().isoformat() if hasattr(datetime, 'now') else None
                }
            }
            
            return {
                "status": "success",
                "message": f"PowerPoint presentation '{presentation_title}' created successfully",
                "filename": filename,
                "file_content": ppt_base64,
                "num_slides": len(slide_outline) + 1,  # +1 for title slide
                "download_url": f"/api/v1/dashboard/presentations/{presentation_title.replace(' ', '_')}/download",
                "widget_data": widget_data
            }
            
        except Exception as e:
            logger.error(f"Error creating PowerPoint presentation: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_create_word_document(self, user_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_word_document function call."""
        try:
            from app.services.widget_export_service import WidgetExportService
            import base64
            
            document_title = arguments.get("document_title", "Document")
            content_sections = arguments.get("content_sections", [])
            subtitle = arguments.get("subtitle")
            upload_to_onedrive = arguments.get("upload_to_onedrive", False)
            onedrive_folder = arguments.get("onedrive_folder", "")
            
            # Create document
            export_service = WidgetExportService()
            doc_bytes = export_service.create_word_document_from_content(
                document_title=document_title,
                content=content_sections,
                subtitle=subtitle
            )
            
            filename = f"{document_title.replace(' ', '_')}.docx"
            
            # If upload to OneDrive is requested
            if upload_to_onedrive:
                token = self._get_microsoft_token(user_id)
                if not token:
                    return {
                        "status": "error",
                        "error": "Microsoft account not connected. Please connect your Microsoft account to upload to OneDrive."
                    }
                
                msgraph_service = get_msgraph_service()
                upload_result = msgraph_service.upload_to_onedrive(
                    token=token,
                    file_bytes=doc_bytes,
                    filename=filename,
                    folder_path=onedrive_folder or "",
                    conflict_behavior="rename"
                )
                
                if upload_result.get("status") == "success":
                    # Create widget data for OneDrive-uploaded Word document
                    widget_data = {
                        "type": "generated-document",
                        "title": f"Word Document: {document_title}",
                        "data": {
                            "document_type": "word",
                            "filename": upload_result.get("filename", filename),
                            "title": document_title,
                            "web_url": upload_result.get("web_url"),
                            "file_id": upload_result.get("file_id"),
                            "onedrive_uploaded": True,
                            "created_at": datetime.now().isoformat() if hasattr(datetime, 'now') else None
                        }
                    }
                    return {
                        "status": "success",
                        "message": f"Word document '{document_title}' created and uploaded to OneDrive",
                        "file_id": upload_result.get("file_id"),
                        "web_url": upload_result.get("web_url"),
                        "filename": upload_result.get("filename"),
                        "widget_data": widget_data
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Failed to upload to OneDrive: {upload_result.get('error')}"
                    }
            
            # Return document as base64 for download
            doc_base64 = base64.b64encode(doc_bytes).decode('utf-8')
            
            # Create widget data for generated Word document
            widget_data = {
                "type": "generated-document",
                "title": f"Word Document: {document_title}",
                "data": {
                    "document_type": "word",
                    "filename": filename,
                    "title": document_title,
                    "file_content": doc_base64,
                    "created_at": datetime.now().isoformat() if hasattr(datetime, 'now') else None
                }
            }
            
            return {
                "status": "success",
                "message": f"Word document '{document_title}' created successfully",
                "filename": filename,
                "file_content": doc_base64,
                "widget_data": widget_data
            }
            
        except Exception as e:
            logger.error(f"Error creating Word document: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_create_pdf_document(self, user_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_pdf_document function call."""
        try:
            from app.services.widget_export_service import WidgetExportService
            import base64
            
            document_title = arguments.get("document_title", "Document")
            content_sections = arguments.get("content_sections", [])
            subtitle = arguments.get("subtitle")
            upload_to_onedrive = arguments.get("upload_to_onedrive", False)
            onedrive_folder = arguments.get("onedrive_folder", "")
            
            # Create PDF
            export_service = WidgetExportService()
            pdf_bytes = export_service.create_pdf_from_content(
                document_title=document_title,
                content=content_sections,
                subtitle=subtitle
            )
            
            filename = f"{document_title.replace(' ', '_')}.pdf"
            
            # If upload to OneDrive is requested
            if upload_to_onedrive:
                token = self._get_microsoft_token(user_id)
                if not token:
                    return {
                        "status": "error",
                        "error": "Microsoft account not connected. Please connect your Microsoft account to upload to OneDrive."
                    }
                
                msgraph_service = get_msgraph_service()
                upload_result = msgraph_service.upload_to_onedrive(
                    token=token,
                    file_bytes=pdf_bytes,
                    filename=filename,
                    folder_path=onedrive_folder or "",
                    conflict_behavior="rename"
                )
                
                if upload_result.get("status") == "success":
                    # Create widget data for OneDrive-uploaded PDF
                    widget_data = {
                        "type": "generated-document",
                        "title": f"PDF Document: {document_title}",
                        "data": {
                            "document_type": "pdf",
                            "filename": upload_result.get("filename", filename),
                            "title": document_title,
                            "web_url": upload_result.get("web_url"),
                            "file_id": upload_result.get("file_id"),
                            "onedrive_uploaded": True,
                            "created_at": datetime.now().isoformat() if hasattr(datetime, 'now') else None
                        }
                    }
                    return {
                        "status": "success",
                        "message": f"PDF document '{document_title}' created and uploaded to OneDrive",
                        "file_id": upload_result.get("file_id"),
                        "web_url": upload_result.get("web_url"),
                        "filename": upload_result.get("filename"),
                        "widget_data": widget_data
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Failed to upload to OneDrive: {upload_result.get('error')}"
                    }
            
            # Return PDF as base64 for download
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Create widget data for generated PDF
            widget_data = {
                "type": "generated-document",
                "title": f"PDF Document: {document_title}",
                "data": {
                    "document_type": "pdf",
                    "filename": filename,
                    "title": document_title,
                    "file_content": pdf_base64,
                    "created_at": datetime.now().isoformat() if hasattr(datetime, 'now') else None
                }
            }
            
            return {
                "status": "success",
                "message": f"PDF document '{document_title}' created successfully",
                "filename": filename,
                "file_content": pdf_base64,
                "widget_data": widget_data
            }
            
        except Exception as e:
            logger.error(f"Error creating PDF document: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_create_excel_spreadsheet(self, user_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_excel_spreadsheet function call."""
        try:
            from app.services.widget_export_service import WidgetExportService
            import base64
            
            spreadsheet_title = arguments.get("spreadsheet_title", "Spreadsheet")
            sheets = arguments.get("sheets", [])
            subtitle = arguments.get("subtitle")
            upload_to_onedrive = arguments.get("upload_to_onedrive", False)
            onedrive_folder = arguments.get("onedrive_folder", "")
            
            # Create spreadsheet
            export_service = WidgetExportService()
            excel_bytes = export_service.create_excel_spreadsheet_from_data(
                spreadsheet_title=spreadsheet_title,
                sheets=sheets,
                subtitle=subtitle
            )
            
            filename = f"{spreadsheet_title.replace(' ', '_')}.xlsx"
            
            # If upload to OneDrive is requested
            if upload_to_onedrive:
                token = self._get_microsoft_token(user_id)
                if not token:
                    return {
                        "status": "error",
                        "error": "Microsoft account not connected. Please connect your Microsoft account to upload to OneDrive."
                    }
                
                msgraph_service = get_msgraph_service()
                upload_result = msgraph_service.upload_to_onedrive(
                    token=token,
                    file_bytes=excel_bytes,
                    filename=filename,
                    folder_path=onedrive_folder or "",
                    conflict_behavior="rename"
                )
                
                if upload_result.get("status") == "success":
                    # Create widget data for OneDrive-uploaded Excel spreadsheet
                    widget_data = {
                        "type": "generated-document",
                        "title": f"Excel Spreadsheet: {spreadsheet_title}",
                        "data": {
                            "document_type": "excel",
                            "filename": upload_result.get("filename", filename),
                            "title": spreadsheet_title,
                            "web_url": upload_result.get("web_url"),
                            "file_id": upload_result.get("file_id"),
                            "onedrive_uploaded": True,
                            "created_at": datetime.now().isoformat() if hasattr(datetime, 'now') else None
                        }
                    }
                    return {
                        "status": "success",
                        "message": f"Excel spreadsheet '{spreadsheet_title}' created and uploaded to OneDrive",
                        "file_id": upload_result.get("file_id"),
                        "web_url": upload_result.get("web_url"),
                        "filename": upload_result.get("filename"),
                        "widget_data": widget_data
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Failed to upload to OneDrive: {upload_result.get('error')}"
                    }
            
            # Return spreadsheet as base64 for download
            excel_base64 = base64.b64encode(excel_bytes).decode('utf-8')
            
            # Create widget data for generated Excel spreadsheet
            widget_data = {
                "type": "generated-document",
                "title": f"Excel Spreadsheet: {spreadsheet_title}",
                "data": {
                    "document_type": "excel",
                    "filename": filename,
                    "title": spreadsheet_title,
                    "file_content": excel_base64,
                    "created_at": datetime.now().isoformat() if hasattr(datetime, 'now') else None
                }
            }
            
            return {
                "status": "success",
                "message": f"Excel spreadsheet '{spreadsheet_title}' created successfully",
                "filename": filename,
                "file_content": excel_base64,
                "widget_data": widget_data
            }
            
        except Exception as e:
            logger.error(f"Error creating Excel spreadsheet: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_generate_image(self, user_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_image function call."""
        try:
            from app.services.content.artwork_service import ArtworkService
            
            prompt = arguments.get("prompt", "")
            size = arguments.get("size", "1024x1024")
            style = arguments.get("style", "natural")
            variations = arguments.get("variations", 1)
            
            artwork_service = ArtworkService()
            results = await artwork_service.generate_artwork(
                prompt=prompt,
                size=size,
                style=style,
                variations=variations
            )
            
            # Create widget data for generated images
            widget_data = {
                "type": "generated-image",
                "title": f"Generated Image: {prompt[:50]}{'...' if len(prompt) > 50 else ''}",
                "data": {
                    "images": results,
                    "prompt": prompt,
                    "style": style,
                    "size": size,
                    "created_at": datetime.now().isoformat() if hasattr(datetime, 'now') else None
                }
            }
            
            return {
                "status": "success",
                "message": f"Generated {len(results)} image(s) successfully",
                "images": results,
                "prompt": prompt,
                "style": style,
                "size": size,
                "widget_data": widget_data
            }
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_search_and_embed_video(self, user_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search_and_embed_video function call."""
        try:
            topic = arguments.get("topic", "")
            platform = arguments.get("video_platform", "any")
            max_results = arguments.get("max_results", 5)
            
            # RECOMMENDED: Use SerpAPI (best option - see explanation below)
            serpapi_key = os.getenv("SERPAPI_KEY")
            if serpapi_key:
                try:
                    # Optional import - install with: pip install google-search-results
                    try:
                        from serpapi import GoogleSearch
                    except ImportError:
                        GoogleSearch = None
                    
                    if not GoogleSearch:
                        raise ImportError("SerpAPI not installed")
                    
                    params = {
                        "q": f"{topic} educational video",
                        "api_key": serpapi_key,
                        "engine": "youtube" if platform == "youtube" else "google",
                        "num": max_results
                    }
                    
                    search = GoogleSearch(params)
                    results = search.get_dict()
                    
                    video_links = []
                    if "video_results" in results:
                        for video in results["video_results"][:max_results]:
                            video_links.append({
                                "title": video.get("title", ""),
                                "url": video.get("link", ""),
                                "platform": "youtube" if "youtube.com" in video.get("link", "") else "other",
                                "description": video.get("snippet", ""),
                                "thumbnail": video.get("thumbnail", "")
                            })
                    
                    return {
                        "status": "success",
                        "message": f"Found {len(video_links)} video(s) for '{topic}'",
                        "videos": video_links,
                        "topic": topic,
                        "platform": platform,
                        "source": "serpapi"
                    }
                except ImportError:
                    logger.warning("SerpAPI not installed. Install with: pip install google-search-results")
                except Exception as e:
                    logger.warning(f"SerpAPI search failed: {str(e)}, falling back to placeholder")
            
            # FALLBACK: YouTube Data API (if SerpAPI not available)
            youtube_api_key = os.getenv("YOUTUBE_API_KEY")
            if youtube_api_key and platform in ["youtube", "any"]:
                try:
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        url = "https://www.googleapis.com/youtube/v3/search"
                        params = {
                            "part": "snippet",
                            "q": f"{topic} educational",
                            "type": "video",
                            "maxResults": max_results,
                            "key": youtube_api_key
                        }
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                video_links = []
                                for item in data.get("items", []):
                                    video_links.append({
                                        "title": item["snippet"]["title"],
                                        "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                                        "platform": "youtube",
                                        "description": item["snippet"]["description"],
                                        "thumbnail": item["snippet"]["thumbnails"]["default"]["url"]
                                    })
                                
                                return {
                                    "status": "success",
                                    "message": f"Found {len(video_links)} video(s) for '{topic}'",
                                    "videos": video_links,
                                    "topic": topic,
                                    "platform": platform,
                                    "source": "youtube_api"
                                }
                except Exception as e:
                    logger.warning(f"YouTube API search failed: {str(e)}, falling back to placeholder")
            
            # PLACEHOLDER: Return structured response if no APIs configured
            video_links = []
            for i in range(min(max_results, 5)):
                video_links.append({
                    "title": f"Educational video about {topic}",
                    "url": f"https://www.youtube.com/watch?v=example{i}",
                    "platform": "youtube",
                    "description": f"Video resource about {topic}",
                    "note": "Configure SERPAPI_KEY or YOUTUBE_API_KEY for real results"
                })
            
            return {
                "status": "success",
                "message": f"Found {len(video_links)} video(s) for '{topic}' (placeholder - configure API keys for real results)",
                "videos": video_links,
                "topic": topic,
                "platform": platform,
                "source": "placeholder"
            }
            
        except Exception as e:
            logger.error(f"Error searching for videos: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_search_and_embed_web_links(self, user_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search_and_embed_web_links function call."""
        try:
            topic = arguments.get("topic", "")
            resource_type = arguments.get("resource_type", "any")
            max_results = arguments.get("max_results", 5)
            
            # RECOMMENDED: Use SerpAPI (best option - combines Google, Bing, etc.)
            serpapi_key = os.getenv("SERPAPI_KEY")
            if serpapi_key:
                try:
                    # Optional import - install with: pip install google-search-results
                    try:
                        from serpapi import GoogleSearch
                    except ImportError:
                        GoogleSearch = None
                    
                    if not GoogleSearch:
                        raise ImportError("SerpAPI not installed")
                    
                    params = {
                        "q": f"{topic} educational resource",
                        "api_key": serpapi_key,
                        "engine": "google",
                        "num": max_results
                    }
                    
                    search = GoogleSearch(params)
                    results = search.get_dict()
                    
                    web_links = []
                    if "organic_results" in results:
                        for result in results["organic_results"][:max_results]:
                            web_links.append({
                                "title": result.get("title", ""),
                                "url": result.get("link", ""),
                                "description": result.get("snippet", ""),
                                "type": resource_type
                            })
                    
                    return {
                        "status": "success",
                        "message": f"Found {len(web_links)} web resource(s) for '{topic}'",
                        "links": web_links,
                        "topic": topic,
                        "resource_type": resource_type,
                        "source": "serpapi"
                    }
                except ImportError:
                    logger.warning("SerpAPI not installed. Install with: pip install google-search-results")
                except Exception as e:
                    logger.warning(f"SerpAPI search failed: {str(e)}, falling back to placeholder")
            
            # FALLBACK: Google Custom Search API
            google_search_key = os.getenv("GOOGLE_SEARCH_API_KEY")
            google_cx = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            if google_search_key and google_cx:
                try:
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        url = "https://www.googleapis.com/customsearch/v1"
                        params = {
                            "key": google_search_key,
                            "cx": google_cx,
                            "q": f"{topic} educational",
                            "num": max_results
                        }
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                web_links = []
                                for item in data.get("items", []):
                                    web_links.append({
                                        "title": item.get("title", ""),
                                        "url": item.get("link", ""),
                                        "description": item.get("snippet", ""),
                                        "type": resource_type
                                    })
                                
                                return {
                                    "status": "success",
                                    "message": f"Found {len(web_links)} web resource(s) for '{topic}'",
                                    "links": web_links,
                                    "topic": topic,
                                    "resource_type": resource_type,
                                    "source": "google_custom_search"
                                }
                except Exception as e:
                    logger.warning(f"Google Custom Search failed: {str(e)}, falling back to placeholder")
            
            # PLACEHOLDER: Return structured response if no APIs configured
            web_links = []
            for i in range(min(max_results, 5)):
                web_links.append({
                    "title": f"Educational resource about {topic}",
                    "url": f"https://example.com/resource/{i}",
                    "description": f"Resource about {topic}",
                    "type": resource_type,
                    "note": "Configure SERPAPI_KEY or GOOGLE_SEARCH_API_KEY for real results"
                })
            
            return {
                "status": "success",
                "message": f"Found {len(web_links)} web resource(s) for '{topic}' (placeholder - configure API keys for real results)",
                "links": web_links,
                "topic": topic,
                "resource_type": resource_type,
                "source": "placeholder"
            }
            
        except Exception as e:
            logger.error(f"Error searching for web links: {str(e)}")
            return {"status": "error", "error": str(e)}

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