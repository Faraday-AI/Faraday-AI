from typing import Dict, List, Optional, Union
import openai
from app.core.config import get_settings
import logging
import json
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class EducationService:
    def __init__(self):
        self.settings = get_settings()
        openai.api_key = self.settings.OPENAI_API_KEY

    async def create_lesson_plan(self, 
                               subject: str,
                               grade_level: str,
                               topic: str,
                               duration: str,
                               learning_objectives: List[str]) -> Dict:
        """
        Generate a detailed lesson plan using AI.
        
        Args:
            subject: Subject area (e.g., "Mathematics", "Science")
            grade_level: Grade level (e.g., "9th Grade", "College")
            topic: Specific topic to cover
            duration: Lesson duration (e.g., "45 minutes", "2 hours")
            learning_objectives: List of learning objectives
            
        Returns:
            Dict containing the lesson plan
        """
        try:
            prompt = self._create_lesson_plan_prompt(
                subject, grade_level, topic, duration, learning_objectives
            )
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert curriculum designer. Create engaging and effective lesson plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            lesson_plan = json.loads(response.choices[0].message.content)
            lesson_plan.update({
                "created_at": datetime.utcnow().isoformat(),
                "subject": subject,
                "grade_level": grade_level,
                "topic": topic,
                "duration": duration
            })
            
            return lesson_plan
            
        except Exception as e:
            logger.error(f"Error creating lesson plan: {str(e)}")
            raise

    async def generate_assessment_questions(self,
                                         subject: str,
                                         topic: str,
                                         difficulty: str,
                                         question_type: str,
                                         num_questions: int) -> Dict:
        """
        Generate assessment questions with answers and explanations.
        
        Args:
            subject: Subject area
            topic: Specific topic
            difficulty: Question difficulty (easy, medium, hard)
            question_type: Type of questions (multiple_choice, short_answer, etc.)
            num_questions: Number of questions to generate
            
        Returns:
            Dict containing questions and answers
        """
        try:
            prompt = self._create_assessment_prompt(
                subject, topic, difficulty, question_type, num_questions
            )
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert assessment designer. Create high-quality educational questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            assessment = json.loads(response.choices[0].message.content)
            assessment.update({
                "created_at": datetime.utcnow().isoformat(),
                "subject": subject,
                "topic": topic,
                "difficulty": difficulty,
                "question_type": question_type
            })
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error generating assessment questions: {str(e)}")
            raise

    async def analyze_student_progress(self,
                                    student_data: Dict,
                                    subject: str,
                                    time_period: str) -> Dict:
        """
        Analyze student progress and provide recommendations.
        
        Args:
            student_data: Dictionary containing student performance data
            subject: Subject area
            time_period: Time period for analysis (e.g., "semester", "year")
            
        Returns:
            Dict containing analysis and recommendations
        """
        try:
            prompt = self._create_progress_analysis_prompt(
                student_data, subject, time_period
            )
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational analyst. Analyze student progress and provide actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            analysis.update({
                "analyzed_at": datetime.utcnow().isoformat(),
                "subject": subject,
                "time_period": time_period
            })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing student progress: {str(e)}")
            raise

    async def create_curriculum_outline(self,
                                     subject: str,
                                     grade_level: str,
                                     duration: str,
                                     learning_standards: List[str]) -> Dict:
        """
        Generate a comprehensive curriculum outline.
        
        Args:
            subject: Subject area
            grade_level: Grade level
            duration: Course duration (e.g., "semester", "year")
            learning_standards: List of learning standards to cover
            
        Returns:
            Dict containing the curriculum outline
        """
        try:
            prompt = self._create_curriculum_prompt(
                subject, grade_level, duration, learning_standards
            )
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert curriculum designer. Create comprehensive and standards-aligned curriculum outlines."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            curriculum = json.loads(response.choices[0].message.content)
            curriculum.update({
                "created_at": datetime.utcnow().isoformat(),
                "subject": subject,
                "grade_level": grade_level,
                "duration": duration
            })
            
            return curriculum
            
        except Exception as e:
            logger.error(f"Error creating curriculum outline: {str(e)}")
            raise

    async def generate_differentiated_instruction(self,
                                               lesson_content: str,
                                               student_profiles: List[Dict]) -> Dict:
        """
        Generate differentiated instruction strategies for diverse learners.
        
        Args:
            lesson_content: Original lesson content
            student_profiles: List of student profiles with learning needs
            
        Returns:
            Dict containing differentiated instruction strategies
        """
        try:
            prompt = self._create_differentiation_prompt(
                lesson_content, student_profiles
            )
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in differentiated instruction. Create strategies to meet diverse learning needs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            strategies = json.loads(response.choices[0].message.content)
            strategies.update({
                "created_at": datetime.utcnow().isoformat(),
                "num_students": len(student_profiles)
            })
            
            return strategies
            
        except Exception as e:
            logger.error(f"Error generating differentiated instruction: {str(e)}")
            raise

    def _create_lesson_plan_prompt(self, subject: str, grade_level: str,
                                 topic: str, duration: str,
                                 learning_objectives: List[str]) -> str:
        """Create a prompt for lesson plan generation."""
        return f"""
        Create a detailed lesson plan for {subject} at {grade_level} level.
        Topic: {topic}
        Duration: {duration}
        
        Learning Objectives:
        {json.dumps(learning_objectives, indent=2)}
        
        Please provide a JSON response with the following structure:
        {{
            "lesson_title": str,
            "materials_needed": List[str],
            "prerequisites": List[str],
            "lesson_steps": List[Dict[str, str]],
            "assessment_methods": List[str],
            "extension_activities": List[str],
            "differentiation_strategies": List[str]
        }}
        """

    def _create_assessment_prompt(self, subject: str, topic: str,
                                difficulty: str, question_type: str,
                                num_questions: int) -> str:
        """Create a prompt for assessment generation."""
        return f"""
        Generate {num_questions} {difficulty} {question_type} questions for {subject} topic: {topic}
        
        Please provide a JSON response with the following structure:
        {{
            "questions": List[Dict[str, Union[str, List[str], Dict[str, str]]]],
            "answer_key": Dict[str, str],
            "explanations": Dict[str, str],
            "learning_objectives_covered": List[str]
        }}
        """

    def _create_progress_analysis_prompt(self, student_data: Dict,
                                       subject: str, time_period: str) -> str:
        """Create a prompt for progress analysis."""
        return f"""
        Analyze the following student progress data for {subject} over {time_period}:
        
        Student Data:
        {json.dumps(student_data, indent=2)}
        
        Please provide a JSON response with the following structure:
        {{
            "overall_progress": float,
            "strengths": List[str],
            "areas_for_improvement": List[str],
            "recommendations": List[str],
            "learning_patterns": Dict[str, str],
            "intervention_suggestions": List[str]
        }}
        """

    def _create_curriculum_prompt(self, subject: str, grade_level: str,
                                duration: str, learning_standards: List[str]) -> str:
        """Create a prompt for curriculum outline generation."""
        return f"""
        Create a comprehensive curriculum outline for {subject} at {grade_level} level.
        Duration: {duration}
        
        Learning Standards:
        {json.dumps(learning_standards, indent=2)}
        
        Please provide a JSON response with the following structure:
        {{
            "course_overview": str,
            "units": List[Dict[str, Union[str, List[str], Dict[str, str]]]],
            "learning_sequence": List[str],
            "assessment_strategies": List[str],
            "resources": List[str],
            "timeline": Dict[str, str]
        }}
        """

    def _create_differentiation_prompt(self, lesson_content: str,
                                    student_profiles: List[Dict]) -> str:
        """Create a prompt for differentiated instruction generation."""
        return f"""
        Create differentiated instruction strategies for the following lesson content:
        
        Lesson Content:
        {lesson_content}
        
        Student Profiles:
        {json.dumps(student_profiles, indent=2)}
        
        Please provide a JSON response with the following structure:
        {{
            "strategies": List[Dict[str, Union[str, List[str], Dict[str, str]]]],
            "accommodations": List[str],
            "modifications": List[str],
            "enrichment_activities": List[str],
            "support_resources": List[str]
        }}
        """ 
