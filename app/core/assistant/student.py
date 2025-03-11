from typing import Dict, Any, List
from app.core.assistant.base import BaseAssistant, AssistantCapability, AssistantContext
import logging

logger = logging.getLogger(__name__)

class StudentAssistant(BaseAssistant):
    """Specialized AI assistant for students."""
    
    def _initialize_capabilities(self):
        """Initialize student-specific capabilities."""
        self.capabilities = {
            "learning_support": AssistantCapability(
                name="learning_support",
                description="Personalized learning assistance and tutoring",
                requires_permissions=["access_learning_support"],
                config={
                    "subject_tutoring": True,
                    "homework_help": True,
                    "study_strategies": True
                }
            ),
            "progress_tracking": AssistantCapability(
                name="progress_tracking",
                description="Track and visualize learning progress",
                requires_permissions=["view_own_progress"],
                config={
                    "goal_setting": True,
                    "achievement_tracking": True,
                    "skill_development": True
                }
            ),
            "study_planning": AssistantCapability(
                name="study_planning",
                description="Create and manage study schedules",
                requires_permissions=["manage_study_plan"],
                config={
                    "schedule_optimization": True,
                    "reminder_system": True,
                    "workload_balancing": True
                }
            ),
            "peer_collaboration": AssistantCapability(
                name="peer_collaboration",
                description="Find and connect with study partners",
                requires_permissions=["use_collaboration_tools"],
                config={
                    "partner_matching": True,
                    "group_formation": True,
                    "project_coordination": True
                }
            )
        }

    async def get_learning_support(
        self,
        subject: str,
        topic: str,
        difficulty_level: str
    ) -> Dict[str, Any]:
        """Get personalized learning support."""
        if not self.capabilities["learning_support"].enabled:
            raise PermissionError("Learning support capability is not enabled")

        try:
            # Generate personalized learning content
            prompt = f"""
            Provide learning support for:
            Subject: {subject}
            Topic: {topic}
            Difficulty Level: {difficulty_level}
            Learning Style: {self.context.preferences.get('learning_style', 'mixed')}

            Include:
            1. Clear explanation of concepts
            2. Relevant examples
            3. Practice problems
            4. Study tips
            5. Common misconceptions
            6. Additional resources
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert tutor specializing in personalized learning."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            return {
                "content": response.choices[0].message.content,
                "metadata": {
                    "subject": subject,
                    "topic": topic,
                    "difficulty": difficulty_level,
                    "learning_style": self.context.preferences.get('learning_style', 'mixed')
                }
            }

        except Exception as e:
            logger.error(f"Error getting learning support: {str(e)}")
            raise

    async def create_study_plan(
        self,
        subjects: List[str],
        goals: List[str],
        available_hours: int
    ) -> Dict[str, Any]:
        """Create personalized study plan."""
        if not self.capabilities["study_planning"].enabled:
            raise PermissionError("Study planning capability is not enabled")

        try:
            # Generate optimized study plan
            prompt = f"""
            Create a personalized study plan for:
            Subjects: {', '.join(subjects)}
            Goals: {', '.join(goals)}
            Available Hours: {available_hours} per week
            Learning Style: {self.context.preferences.get('learning_style', 'mixed')}
            Peak Performance Time: {self.context.preferences.get('peak_time', 'flexible')}

            Include:
            1. Weekly schedule
            2. Subject prioritization
            3. Break intervals
            4. Progress checkpoints
            5. Review strategies
            6. Flexibility options
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert in educational planning and time management."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            return {
                "plan": response.choices[0].message.content,
                "metadata": {
                    "subjects": subjects,
                    "goals": goals,
                    "available_hours": available_hours,
                    "preferences": {
                        "learning_style": self.context.preferences.get('learning_style'),
                        "peak_time": self.context.preferences.get('peak_time')
                    }
                }
            }

        except Exception as e:
            logger.error(f"Error creating study plan: {str(e)}")
            raise

    async def track_progress(
        self,
        subject: str,
        timeframe: str = "weekly"
    ) -> Dict[str, Any]:
        """Track and analyze learning progress."""
        if not self.capabilities["progress_tracking"].enabled:
            raise PermissionError("Progress tracking capability is not enabled")

        try:
            # Analyze progress data
            progress_data = self.context.session_data.get("progress_data", {})
            
            prompt = f"""
            Analyze learning progress for:
            Subject: {subject}
            Timeframe: {timeframe}
            Progress Data: {progress_data}

            Provide:
            1. Achievement summary
            2. Skill development progress
            3. Areas for improvement
            4. Next learning goals
            5. Celebration points
            6. Growth opportunities
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert in learning analytics and student development."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            return {
                "analysis": response.choices[0].message.content,
                "metrics": self._calculate_progress_metrics(progress_data),
                "recommendations": self._generate_learning_recommendations(response.choices[0].message.content)
            }

        except Exception as e:
            logger.error(f"Error tracking progress: {str(e)}")
            raise

    async def find_study_partners(
        self,
        subject: str,
        topic: str,
        group_size: int = 2
    ) -> Dict[str, Any]:
        """Find compatible study partners."""
        if not self.capabilities["peer_collaboration"].enabled:
            raise PermissionError("Peer collaboration capability is not enabled")

        try:
            # Match with potential study partners
            student_data = self.context.session_data.get("student_data", {})
            
            prompt = f"""
            Find study partners for:
            Subject: {subject}
            Topic: {topic}
            Group Size: {group_size}
            Student Profile: {student_data}

            Consider:
            1. Learning style compatibility
            2. Skill level complementarity
            3. Schedule alignment
            4. Communication preferences
            5. Collaboration history
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert in educational collaboration and team formation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            return {
                "recommendations": response.choices[0].message.content,
                "matching_criteria": self._extract_matching_criteria(response.choices[0].message.content)
            }

        except Exception as e:
            logger.error(f"Error finding study partners: {str(e)}")
            raise

    def _calculate_progress_metrics(self, progress_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate learning progress metrics."""
        try:
            metrics = {
                "completion_rate": 0.0,
                "mastery_level": 0.0,
                "engagement_score": 0.0,
                "consistency_score": 0.0
            }

            if progress_data:
                # Calculate completion rate
                total_tasks = len(progress_data.get("tasks", []))
                completed_tasks = len([t for t in progress_data.get("tasks", []) if t.get("completed")])
                metrics["completion_rate"] = completed_tasks / total_tasks if total_tasks > 0 else 0.0

                # Calculate mastery level
                assessment_scores = [a.get("score", 0) for a in progress_data.get("assessments", [])]
                metrics["mastery_level"] = sum(assessment_scores) / len(assessment_scores) if assessment_scores else 0.0

                # Calculate engagement score
                engagement_factors = progress_data.get("engagement_factors", {})
                metrics["engagement_score"] = sum(engagement_factors.values()) / len(engagement_factors) if engagement_factors else 0.0

                # Calculate consistency score
                study_sessions = progress_data.get("study_sessions", [])
                if study_sessions:
                    session_intervals = []
                    for i in range(1, len(study_sessions)):
                        interval = study_sessions[i]["start_time"] - study_sessions[i-1]["end_time"]
                        session_intervals.append(interval)
                    avg_interval = sum(session_intervals) / len(session_intervals)
                    metrics["consistency_score"] = 1.0 / (1.0 + avg_interval)  # Normalize to 0-1

            return metrics

        except Exception as e:
            logger.error(f"Error calculating progress metrics: {str(e)}")
            return {
                "completion_rate": 0.0,
                "mastery_level": 0.0,
                "engagement_score": 0.0,
                "consistency_score": 0.0
            }

    def _generate_learning_recommendations(self, analysis: str) -> List[Dict[str, Any]]:
        """Generate structured learning recommendations."""
        try:
            recommendations = []
            current_section = None

            for line in analysis.split("\n"):
                if line.strip().startswith(("Recommendation:", "Action:", "Focus:")):
                    if current_section:
                        recommendations.append(current_section)
                    current_section = {
                        "title": line.split(":", 1)[1].strip(),
                        "steps": [],
                        "resources": [],
                        "priority": "medium"
                    }
                elif current_section and line.strip().startswith("- "):
                    current_section["steps"].append(line.strip()[2:])
                elif current_section and line.strip().startswith("Resource:"):
                    current_section["resources"].append(line.split(":", 1)[1].strip())

            if current_section:
                recommendations.append(current_section)

            return recommendations

        except Exception as e:
            logger.error(f"Error generating learning recommendations: {str(e)}")
            return []

    def _extract_matching_criteria(self, response: str) -> Dict[str, Any]:
        """Extract structured matching criteria from response."""
        try:
            criteria = {
                "learning_style_match": [],
                "skill_complementarity": [],
                "schedule_compatibility": [],
                "communication_preferences": []
            }

            current_category = None
            for line in response.split("\n"):
                line = line.strip()
                if line.endswith(":"):
                    current_category = line[:-1].lower().replace(" ", "_")
                elif current_category and line.startswith("- "):
                    if current_category in criteria:
                        criteria[current_category].append(line[2:])

            return criteria

        except Exception as e:
            logger.error(f"Error extracting matching criteria: {str(e)}")
            return {} 