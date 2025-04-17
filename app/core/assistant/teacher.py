from typing import Dict, Any, List
from app.core.assistant.base import BaseAssistant, AssistantCapability, AssistantContext
from app.services.ai.ai_group import AIGroupAnalysis
from app.services.ai.ai_analytics import AIAnalytics
import logging

logger = logging.getLogger(__name__)

class TeacherAssistant(BaseAssistant):
    """Specialized AI assistant for teachers."""
    
    def __init__(self, context: AssistantContext):
        super().__init__(context)
        self.group_analysis = AIGroupAnalysis()
        self.analytics = AIAnalytics()

    def _initialize_capabilities(self):
        """Initialize teacher-specific capabilities."""
        self.capabilities = {
            "lesson_planning": AssistantCapability(
                name="lesson_planning",
                description="Create and modify lesson plans with AI assistance",
                requires_permissions=["create_lesson_plans"],
                config={
                    "templates_enabled": True,
                    "ai_enhancement": True,
                    "collaborative_editing": True
                }
            ),
            "student_analytics": AssistantCapability(
                name="student_analytics",
                description="Analyze student performance and behavior patterns",
                requires_permissions=["view_student_data"],
                config={
                    "real_time_monitoring": True,
                    "predictive_analytics": True,
                    "intervention_suggestions": True
                }
            ),
            "group_dynamics": AssistantCapability(
                name="group_dynamics",
                description="Monitor and analyze group interactions",
                requires_permissions=["monitor_groups"],
                config={
                    "real_time_analysis": True,
                    "social_network_analysis": True,
                    "intervention_alerts": True
                }
            ),
            "content_creation": AssistantCapability(
                name="content_creation",
                description="Generate educational content and materials",
                requires_permissions=["create_content"],
                config={
                    "multimedia_generation": True,
                    "differentiation_support": True,
                    "accessibility_features": True
                }
            ),
            "assessment_tools": AssistantCapability(
                name="assessment_tools",
                description="Create and analyze assessments",
                requires_permissions=["manage_assessments"],
                config={
                    "auto_grading": True,
                    "question_generation": True,
                    "feedback_enhancement": True
                }
            )
        }

    async def create_lesson_plan(
        self,
        subject: str,
        grade_level: str,
        duration: int,
        objectives: List[str]
    ) -> Dict[str, Any]:
        """Create an AI-enhanced lesson plan."""
        if not self.capabilities["lesson_planning"].enabled:
            raise PermissionError("Lesson planning capability is not enabled")

        try:
            # Generate lesson plan using AI
            prompt = f"""
            Create a detailed lesson plan for:
            Subject: {subject}
            Grade Level: {grade_level}
            Duration: {duration} minutes
            Learning Objectives: {', '.join(objectives)}

            Include:
            1. Essential questions
            2. Learning activities
            3. Assessment strategies
            4. Differentiation approaches
            5. Required materials
            6. Technology integration
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert curriculum designer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            return {
                "content": response.choices[0].message.content,
                "metadata": {
                    "subject": subject,
                    "grade_level": grade_level,
                    "duration": duration,
                    "objectives": objectives,
                    "generated_at": self.context.session_data.get("timestamp")
                }
            }

        except Exception as e:
            logger.error(f"Error creating lesson plan: {str(e)}")
            raise

    async def analyze_student_performance(
        self,
        student_id: str,
        timeframe: str = "recent"
    ) -> Dict[str, Any]:
        """Analyze individual student performance."""
        if not self.capabilities["student_analytics"].enabled:
            raise PermissionError("Student analytics capability is not enabled")

        try:
            # Get student data and analyze
            analysis = await self.analytics.analyze_student_performance(
                student_id=student_id,
                timeframe=timeframe,
                context=self.context.session_data
            )

            # Generate AI insights
            prompt = f"""
            Analyze student performance data and provide:
            1. Key strengths and areas for improvement
            2. Learning pattern insights
            3. Personalized recommendations
            4. Suggested interventions if needed
            5. Progress tracking metrics

            Data: {analysis}
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert educational analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )

            return {
                "analysis": analysis,
                "ai_insights": response.choices[0].message.content,
                "recommendations": self._extract_recommendations(response.choices[0].message.content)
            }

        except Exception as e:
            logger.error(f"Error analyzing student performance: {str(e)}")
            raise

    async def monitor_group_activity(
        self,
        group_id: str,
        activity_type: str
    ) -> Dict[str, Any]:
        """Monitor and analyze group activities."""
        if not self.capabilities["group_dynamics"].enabled:
            raise PermissionError("Group dynamics capability is not enabled")

        try:
            # Start real-time monitoring
            monitoring_data = await self.group_analysis.start_real_time_monitoring(
                session_id=group_id,
                group_data={
                    "activity_type": activity_type,
                    "context": self.context.session_data
                }
            )

            return {
                "monitoring_id": group_id,
                "status": "active",
                "initial_metrics": monitoring_data,
                "websocket_url": f"/ws/group/{group_id}"
            }

        except Exception as e:
            logger.error(f"Error monitoring group activity: {str(e)}")
            raise

    async def generate_educational_content(
        self,
        topic: str,
        content_type: str,
        difficulty_level: str,
        accessibility_requirements: List[str] = None
    ) -> Dict[str, Any]:
        """Generate educational content with AI assistance."""
        if not self.capabilities["content_creation"].enabled:
            raise PermissionError("Content creation capability is not enabled")

        try:
            # Generate content using AI
            prompt = f"""
            Create educational content for:
            Topic: {topic}
            Type: {content_type}
            Difficulty: {difficulty_level}
            Accessibility: {', '.join(accessibility_requirements or [])}

            Include:
            1. Main content
            2. Interactive elements
            3. Visual descriptions
            4. Assessment components
            5. Differentiation options
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            return {
                "content": response.choices[0].message.content,
                "metadata": {
                    "topic": topic,
                    "type": content_type,
                    "difficulty": difficulty_level,
                    "accessibility": accessibility_requirements,
                    "generated_at": self.context.session_data.get("timestamp")
                }
            }

        except Exception as e:
            logger.error(f"Error generating educational content: {str(e)}")
            raise

    def _extract_recommendations(self, ai_response: str) -> List[Dict[str, Any]]:
        """Extract structured recommendations from AI response."""
        try:
            # Split response into sections
            sections = ai_response.split("\n")
            recommendations = []

            current_rec = None
            for line in sections:
                if line.strip().startswith(("Recommendation:", "Suggestion:", "Action:")):
                    if current_rec:
                        recommendations.append(current_rec)
                    current_rec = {
                        "title": line.split(":", 1)[1].strip(),
                        "details": [],
                        "priority": "medium"
                    }
                elif current_rec and line.strip():
                    current_rec["details"].append(line.strip())
                    if "urgent" in line.lower() or "immediate" in line.lower():
                        current_rec["priority"] = "high"

            if current_rec:
                recommendations.append(current_rec)

            return recommendations

        except Exception as e:
            logger.error(f"Error extracting recommendations: {str(e)}")
            return [] 