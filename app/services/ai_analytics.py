from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import openai
from app.core.config import get_settings
import logging
from datetime import datetime, timedelta
from functools import lru_cache
import asyncio
import hashlib
import json
from collections import defaultdict
import time
from app.core.cache import Cache
from app.core.metrics import MetricsCollector
import os
import joblib
import mediapipe as mp
import httpx
from openai import OpenAI

logger = logging.getLogger(__name__)
settings = get_settings()
metrics = MetricsCollector()
cache = Cache()

# Rate limiting configuration
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds

class RateLimiter:
    def __init__(self, requests_per_window: int, window_seconds: int):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_rate_limited(self, client_id: str) -> bool:
        """Check if the client has exceeded the rate limit."""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean up old requests
        self.requests[client_id] = [t for t in self.requests[client_id] if t > window_start]
        
        # Check if rate limit is exceeded
        if len(self.requests[client_id]) >= self.requests_per_window:
            return True
            
        # Add new request
        self.requests[client_id].append(now)
        return False

    def get_remaining_requests(self, client_id: str) -> int:
        """Get the number of remaining requests for the client."""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean up old requests
        self.requests[client_id] = [t for t in self.requests[client_id] if t > window_start]
        
        return max(0, self.requests_per_window - len(self.requests[client_id]))

rate_limiter = RateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW)

class PhysicalEducationAI:
    """AI service specifically designed for Physical Education assistance."""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.GPT_MODEL
        self._init_pe_prompts()
        self._init_ml_models()

    def _init_ml_models(self):
        """Initialize ML models for various features."""
        # Get the base directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Movement analysis model
        model_path = os.path.join(base_dir, 'models', 'movement_analysis.h5')
        if not os.path.exists(model_path):
            # Create a simple model if it doesn't exist
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(10, activation='relu', input_shape=(10,)),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            model.save(model_path)
        
        self.movement_model = tf.keras.models.load_model(model_path)
        
        # Activity adaptation model
        adaptation_path = os.path.join(base_dir, 'models', 'activity_adaptation.joblib')
        if not os.path.exists(adaptation_path):
            # Create a simple model if it doesn't exist
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            joblib.dump(model, adaptation_path)
        
        self.adaptation_model = joblib.load(adaptation_path)
        
        # Assessment model
        assessment_path = os.path.join(base_dir, 'models', 'skill_assessment.joblib')
        if not os.path.exists(assessment_path):
            # Create a simple model if it doesn't exist
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            joblib.dump(model, assessment_path)
        
        self.assessment_model = joblib.load(assessment_path)

    def _init_pe_prompts(self):
        """Initialize specialized prompts for physical education."""
        self.prompts = {
            "lesson_planning": """As a physical education expert, help create a lesson plan for:
Topic: {topic}
Grade Level: {grade_level}
Duration: {duration}
Include warm-up activities, main exercises, cool-down, and safety considerations.""",
            
            "movement_instruction": """Create detailed movement instructions for:
Activity: {activity}
Skill Level: {skill_level}
Include proper form, common mistakes to avoid, and progression steps.""",
            
            "activity_design": """Design a physical education activity for:
Focus Area: {focus_area}
Grade Level: {grade_level}
Available Equipment: {equipment}
Include safety guidelines, modifications for different ability levels, and assessment criteria.""",
            
            "fitness_assessment": """Create a fitness assessment plan for:
Grade Level: {grade_level}
Focus Areas: {focus_areas}
Include measurement methods, safety protocols, and progress tracking.""",

            "movement_analysis": """Analyze the following movement data:
Activity: {activity}
Data Points: {data_points}
Provide feedback on form, suggest improvements, and identify potential risks.""",

            "activity_adaptation": """Adapt the following activity for:
Original Activity: {activity}
Student Needs: {needs}
Environmental Factors: {environment}
Provide modified versions with different difficulty levels and safety considerations.""",

            "health_wellness": """Create a health and wellness plan for:
Student Profile: {profile}
Goals: {goals}
Current Level: {current_level}
Include nutrition guidance, hydration recommendations, and recovery strategies.""",

            "classroom_management": """Optimize classroom management for:
Class Size: {size}
Available Space: {space}
Equipment: {equipment}
Provide group formation strategies, space utilization tips, and time management suggestions.""",

            "skill_assessment": """Assess student skills for:
Activity: {activity}
Student Performance: {performance}
Previous Assessments: {previous}
Provide detailed analysis, progress tracking, and goal setting recommendations.""",

            "curriculum_integration": """Integrate physical education with:
Subject: {subject}
Grade Level: {grade_level}
Standards: {standards}
Create cross-curricular connections and resource recommendations.""",

            "safety_analysis": """Analyze safety considerations for:
Activity: {activity}
Environment: {environment}
Equipment: {equipment}
Provide risk assessment, safety protocols, and emergency procedures.""",

            "professional_development": """Create a professional development plan for:
Teacher Experience: {experience}
Focus Areas: {focus_areas}
Goals: {goals}
Provide teaching strategy suggestions, resource recommendations, and growth tracking.""",
        }

    async def generate_lesson_plan(self, topic: str, grade_level: str, duration: str) -> Dict[str, Any]:
        """Generate a PE lesson plan."""
        prompt = self.prompts["lesson_planning"].format(
            topic=topic,
            grade_level=grade_level,
            duration=duration
        )
        
        response = await self._get_ai_response(prompt)
        return {
            "lesson_plan": response,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "topic": topic,
                "grade_level": grade_level,
                "duration": duration
            }
        }

    async def create_movement_instruction(self, activity: str, skill_level: str) -> Dict[str, Any]:
        """Create detailed movement instructions."""
        prompt = self.prompts["movement_instruction"].format(
            activity=activity,
            skill_level=skill_level
        )
        
        response = await self._get_ai_response(prompt)
        return {
            "instructions": response,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "activity": activity,
                "skill_level": skill_level
            }
        }

    async def design_activity(self, focus_area: str, grade_level: str, equipment: list) -> Dict[str, Any]:
        """Design a PE activity."""
        prompt = self.prompts["activity_design"].format(
            focus_area=focus_area,
            grade_level=grade_level,
            equipment=", ".join(equipment)
        )
        
        response = await self._get_ai_response(prompt)
        return {
            "activity_design": response,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "focus_area": focus_area,
                "grade_level": grade_level,
                "equipment": equipment
            }
        }

    async def create_fitness_assessment(self, grade_level: str, focus_areas: list) -> Dict[str, Any]:
        """Create a fitness assessment plan."""
        prompt = self.prompts["fitness_assessment"].format(
            grade_level=grade_level,
            focus_areas=", ".join(focus_areas)
        )
        
        response = await self._get_ai_response(prompt)
        return {
            "assessment_plan": response,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "grade_level": grade_level,
                "focus_areas": focus_areas
            }
        }

    async def analyze_movement(self, activity: str, data_points: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze movement patterns and provide feedback."""
        # Process video data using MediaPipe
        mp_pose = mp.solutions.pose
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            results = pose.process(data_points['video_data'])
            
        # Get AI feedback
        prompt = self.prompts["movement_analysis"].format(
            activity=activity,
            data_points=json.dumps(data_points)
        )
        
        ai_feedback = await self._get_ai_response(prompt)
        
        return {
            "analysis": {
                "pose_data": results.pose_landmarks,
                "ai_feedback": ai_feedback,
                "recommendations": self._generate_movement_recommendations(results)
            },
            "timestamp": datetime.now().isoformat()
        }

    async def adapt_activity(self, activity: str, needs: Dict[str, Any], environment: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt activities based on student needs and environment."""
        # Use ML model for initial adaptation
        adaptation_features = self._prepare_adaptation_features(activity, needs, environment)
        base_adaptation = self.adaptation_model.predict([adaptation_features])[0]
        
        # Get AI-enhanced adaptations
        prompt = self.prompts["activity_adaptation"].format(
            activity=activity,
            needs=json.dumps(needs),
            environment=json.dumps(environment)
        )
        
        ai_adaptations = await self._get_ai_response(prompt)
        
        return {
            "adaptations": {
                "base_adaptation": base_adaptation,
                "ai_enhancements": ai_adaptations,
                "safety_considerations": self._generate_safety_guidelines(activity, needs)
            },
            "timestamp": datetime.now().isoformat()
        }

    async def create_health_plan(self, profile: Dict[str, Any], goals: List[str], current_level: str) -> Dict[str, Any]:
        """Create personalized health and wellness plans."""
        prompt = self.prompts["health_wellness"].format(
            profile=json.dumps(profile),
            goals=json.dumps(goals),
            current_level=current_level
        )
        
        plan = await self._get_ai_response(prompt)
        
        return {
            "health_plan": plan,
            "tracking_metrics": self._generate_health_metrics(goals),
            "timestamp": datetime.now().isoformat()
        }

    async def optimize_classroom(self, size: int, space: Dict[str, Any], equipment: List[str]) -> Dict[str, Any]:
        """Optimize classroom management and organization."""
        prompt = self.prompts["classroom_management"].format(
            size=size,
            space=json.dumps(space),
            equipment=json.dumps(equipment)
        )
        
        optimization = await self._get_ai_response(prompt)
        
        return {
            "optimization_plan": optimization,
            "group_suggestions": self._generate_group_formations(size, equipment),
            "timestamp": datetime.now().isoformat()
        }

    async def assess_skills(self, activity: str, performance: Dict[str, Any], previous: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess student skills and track progress."""
        # Use ML model for initial assessment
        assessment_features = self._prepare_assessment_features(performance, previous)
        base_assessment = self.assessment_model.predict([assessment_features])[0]
        
        # Get AI-enhanced assessment
        prompt = self.prompts["skill_assessment"].format(
            activity=activity,
            performance=json.dumps(performance),
            previous=json.dumps(previous)
        )
        
        ai_assessment = await self._get_ai_response(prompt)
        
        return {
            "assessment": {
                "base_score": base_assessment,
                "detailed_analysis": ai_assessment,
                "progress_tracking": self._track_progress(previous, base_assessment),
                "goal_recommendations": self._generate_goals(base_assessment)
            },
            "timestamp": datetime.now().isoformat()
        }

    async def integrate_curriculum(self, subject: str, grade_level: str, standards: List[str]) -> Dict[str, Any]:
        """Integrate PE with other subjects and standards."""
        prompt = self.prompts["curriculum_integration"].format(
            subject=subject,
            grade_level=grade_level,
            standards=json.dumps(standards)
        )
        
        integration = await self._get_ai_response(prompt)
        
        return {
            "integration_plan": integration,
            "resource_recommendations": self._generate_resources(subject, standards),
            "timestamp": datetime.now().isoformat()
        }

    async def analyze_safety(self, activity: str, environment: Dict[str, Any], equipment: List[str]) -> Dict[str, Any]:
        """Analyze safety considerations and provide guidelines."""
        prompt = self.prompts["safety_analysis"].format(
            activity=activity,
            environment=json.dumps(environment),
            equipment=json.dumps(equipment)
        )
        
        safety_analysis = await self._get_ai_response(prompt)
        
        return {
            "safety_analysis": safety_analysis,
            "risk_assessment": self._assess_risks(activity, environment, equipment),
            "emergency_procedures": self._generate_emergency_procedures(activity),
            "timestamp": datetime.now().isoformat()
        }

    async def create_professional_plan(self, experience: str, focus_areas: List[str], goals: List[str]) -> Dict[str, Any]:
        """Create professional development plans."""
        prompt = self.prompts["professional_development"].format(
            experience=experience,
            focus_areas=json.dumps(focus_areas),
            goals=json.dumps(goals)
        )
        
        development_plan = await self._get_ai_response(prompt)
        
        return {
            "development_plan": development_plan,
            "resource_recommendations": self._generate_professional_resources(focus_areas),
            "tracking_metrics": self._generate_professional_metrics(goals),
            "timestamp": datetime.now().isoformat()
        }

    def _prepare_adaptation_features(self, activity: str, needs: Dict[str, Any], environment: Dict[str, Any]) -> np.ndarray:
        """Prepare features for activity adaptation model."""
        # Implementation details for feature preparation
        pass

    def _generate_movement_recommendations(self, pose_results) -> List[str]:
        """Generate movement recommendations based on pose analysis."""
        # Implementation details for movement recommendations
        pass

    def _generate_safety_guidelines(self, activity: str, needs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate safety guidelines for adapted activities."""
        # Implementation details for safety guidelines
        pass

    def _generate_health_metrics(self, goals: List[str]) -> Dict[str, Any]:
        """Generate health and wellness tracking metrics."""
        # Implementation details for health metrics
        pass

    def _generate_group_formations(self, size: int, equipment: List[str]) -> List[Dict[str, Any]]:
        """Generate optimal group formations."""
        # Implementation details for group formations
        pass

    def _prepare_assessment_features(self, performance: Dict[str, Any], previous: List[Dict[str, Any]]) -> np.ndarray:
        """Prepare features for skill assessment model."""
        # Implementation details for assessment features
        pass

    def _track_progress(self, previous: List[Dict[str, Any]], current: float) -> Dict[str, Any]:
        """Track student progress over time."""
        # Implementation details for progress tracking
        pass

    def _generate_goals(self, assessment: float) -> List[Dict[str, Any]]:
        """Generate personalized goals based on assessment."""
        # Implementation details for goal generation
        pass

    def _generate_resources(self, subject: str, standards: List[str]) -> List[Dict[str, Any]]:
        """Generate resource recommendations for curriculum integration."""
        # Implementation details for resource generation
        pass

    def _assess_risks(self, activity: str, environment: Dict[str, Any], equipment: List[str]) -> Dict[str, Any]:
        """Assess risks for activities."""
        # Implementation details for risk assessment
        pass

    def _generate_emergency_procedures(self, activity: str) -> Dict[str, Any]:
        """Generate emergency procedures for activities."""
        # Implementation details for emergency procedures
        pass

    def _generate_professional_resources(self, focus_areas: List[str]) -> List[Dict[str, Any]]:
        """Generate professional development resources."""
        # Implementation details for professional resources
        pass

    def _generate_professional_metrics(self, goals: List[str]) -> Dict[str, Any]:
        """Generate professional development tracking metrics."""
        # Implementation details for professional metrics
        pass

    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from OpenAI with error handling and rate limiting."""
        try:
            if rate_limiter.is_rate_limited("default"):
                raise Exception("Rate limit exceeded. Please try again later.")

            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert physical education teacher with years of experience in developing effective, safe, and engaging PE activities."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            raise

    async def collect_usage_data(self, interaction_type: str, metadata: Dict[str, Any]) -> None:
        """Collect anonymous usage data for grant proposals and improvement."""
        try:
            usage_data = {
                "timestamp": datetime.now().isoformat(),
                "interaction_type": interaction_type,
                "metadata": metadata,
                # No personal or student data collected
            }
            
            # Log for analysis (implement proper analytics storage later)
            logger.info(f"Usage data collected: {json.dumps(usage_data)}")
            
        except Exception as e:
            logger.error(f"Error collecting usage data: {str(e)}")
            # Non-critical error, don't raise

class AIAnalytics:
    def __init__(self):
        # Create a custom httpx client without proxy settings
        http_client = httpx.Client(
            base_url="https://api.openai.com/v1",
            follow_redirects=True,
            timeout=30.0
        )
            
        # Initialize OpenAI client with custom http client
        self.openai_client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            http_client=http_client
        )
        self.model = settings.GPT_MODEL
        self.scaler = StandardScaler()
        self.cache_ttl = 3600  # 1 hour cache TTL
        self._load_models()

    def _generate_cache_key(self, data: Dict[str, Any], analysis_type: str) -> str:
        """Generate a unique cache key for the analysis."""
        # Sort the data to ensure consistent keys
        sorted_data = json.dumps(data, sort_keys=True)
        # Create a hash of the data and analysis type
        key_data = f"{analysis_type}:{sorted_data}".encode('utf-8')
        return hashlib.sha256(key_data).hexdigest()

    def _validate_student_data(self, student_data: Dict[str, Any]) -> None:
        """Validate student data structure and values."""
        required_fields = {
            'student_id': str,
            'grade': (int, float),
            'subjects': list,
            'attendance_rate': (int, float),
            'previous_grades': dict,
            'lesson_history': list
        }

        for field, field_type in required_fields.items():
            if field not in student_data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(student_data[field], field_type):
                raise ValueError(f"Invalid type for {field}: expected {field_type}")

        # Validate numeric ranges
        if not 0 <= student_data['attendance_rate'] <= 1:
            raise ValueError("attendance_rate must be between 0 and 1")

        # Validate lesson history
        for lesson in student_data['lesson_history']:
            if not isinstance(lesson, dict):
                raise ValueError("Each lesson in lesson_history must be a dictionary")
            if 'score' not in lesson or not 0 <= lesson['score'] <= 100:
                raise ValueError("Lesson scores must be between 0 and 100")

    def _validate_classroom_data(self, classroom_data: Dict[str, Any]) -> None:
        """Validate classroom data structure and values."""
        required_fields = {
            'class_size': int,
            'subject': str,
            'average_score': (int, float),
            'participation_rate': (int, float)
        }

        for field, field_type in required_fields.items():
            if field not in classroom_data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(classroom_data[field], field_type):
                raise ValueError(f"Invalid type for {field}: expected {field_type}")

        # Validate numeric ranges
        if not 0 <= classroom_data['participation_rate'] <= 1:
            raise ValueError("participation_rate must be between 0 and 1")
        if not 0 <= classroom_data['average_score'] <= 100:
            raise ValueError("average_score must be between 0 and 100")

    async def analyze_student_performance(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze student performance and provide recommendations."""
        try:
            # Validate input data
            self._validate_student_data(student_data)
            
            # Generate cache key
            cache_key = self._generate_cache_key(student_data, "performance")
            
            # Check cache first
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info("Retrieved performance analysis from cache")
                return cached_result

            # Prepare features for prediction
            features = self._prepare_features(student_data)
            
            # Get prediction with retry logic
            max_retries = 3
            retry_delay = 1  # seconds
            for attempt in range(max_retries):
                try:
                    prediction = self.performance_model.predict(features)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

            # Get AI insights with retry logic
            prompt = self._generate_performance_prompt(student_data, prediction[0])
            for attempt in range(max_retries):
                try:
                    response = await self.openai_client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

            result = {
                "prediction_score": float(prediction[0]),
                "ai_analysis": response.choices[0].message.content,
                "recommendations": self._generate_recommendations(response.choices[0].message.content)
            }
            
            # Cache the result
            await cache.set(cache_key, result, self.cache_ttl)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in analyze_student_performance: {str(e)}", exc_info=True)
            raise

    async def analyze_behavior_patterns(self, student_data: Dict[str, Any], classroom_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze student behavior patterns and engagement levels."""
        try:
            # Validate input data
            self._validate_student_data(student_data)
            self._validate_classroom_data(classroom_data)
            
            # Generate cache key
            cache_key = self._generate_cache_key(
                {"student": student_data, "classroom": classroom_data},
                "behavior"
            )
            
            # Check cache first
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info("Retrieved behavior analysis from cache")
                return cached_result

            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(student_data, classroom_data)
            
            # Prepare prompt with metrics
            prompt = f"""Analyze the following student behavior patterns and engagement levels:

Student Data:
- ID: {student_data['student_id']}
- Grade: {student_data['grade']}
- Attendance Rate: {student_data['attendance_rate']*100}%
- Previous Grades: {json.dumps(student_data['previous_grades'])}

Classroom Data:
- Class Size: {classroom_data['class_size']}
- Subject: {classroom_data['subject']}
- Average Score: {classroom_data['average_score']}%
- Participation Rate: {classroom_data['participation_rate']*100}%

Engagement Score: {engagement_score:.2f}

Please provide a comprehensive analysis covering:
1. Behavior patterns
2. Engagement level
3. Learning style effectiveness
4. Classroom interaction insights
5. Recommendations for improvement

Format the response in a clear, structured manner with specific examples and actionable insights."""

            # Get AI response with retry logic
            max_retries = 3
            retry_delay = 1  # seconds
            for attempt in range(max_retries):
                try:
                    response = await self.openai_client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=1000
                    )
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

            result = {
                "engagement_score": engagement_score,
                "analysis": response.choices[0].message.content,
                "recommendations": self._generate_recommendations(response.choices[0].message.content)
            }
            
            # Cache the result
            await cache.set(cache_key, result, self.cache_ttl)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in analyze_behavior_patterns: {str(e)}", exc_info=True)
            raise

    async def analyze_group_dynamics(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze group dynamics and learning patterns."""
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(group_data, "group_dynamics")
            
            # Check cache first
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info("Retrieved group dynamics analysis from cache")
                return cached_result
            
            # Calculate group metrics first
            metrics = self._calculate_group_metrics(group_data)
            
            # Prepare prompt with metrics
            prompt = f"""Analyze the following group dynamics and learning patterns:

Group Composition:
- Total Students: {group_data['composition']['total_students']}
- Grade Level: {group_data['composition']['grade_level']}
- Subject: {group_data['composition']['subject']}
- Learning Styles: {', '.join(group_data['composition']['diversity_metrics']['learning_styles'])}
- Performance Levels: {', '.join(group_data['composition']['diversity_metrics']['performance_levels'])}

Interaction Patterns:
- Group Work Frequency: {group_data['interaction_patterns']['group_work_frequency']}
- Collaboration Level: {group_data['interaction_patterns']['collaboration_level']}
- Peer Learning: {group_data['interaction_patterns']['peer_learning']}

Learning Outcomes:
- Average Performance: {group_data['learning_outcomes']['average_performance']}%
- Participation Rate: {group_data['learning_outcomes']['participation_rate']*100}%
- Completion Rate: {group_data['learning_outcomes']['completion_rate']*100}%

Group Metrics:
- Diversity Score: {metrics['diversity_score']:.2f}
- Interaction Score: {metrics['interaction_score']:.2f}
- Performance Score: {metrics['performance_score']:.2f}
- Overall Score: {metrics['overall_score']:.2f}

Please provide a comprehensive analysis covering:
1. Group dynamics analysis
2. Learning pattern assessment
3. Interaction effectiveness
4. Performance metrics
5. Optimization recommendations

Format the response in a clear, structured manner with specific examples and actionable insights."""

            # Get AI response with retry logic
            max_retries = 3
            retry_delay = 1  # seconds
            for attempt in range(max_retries):
                try:
                    response = await self.openai_client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=1000
                    )
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

            # Process response
            analysis = response.choices[0].message.content
            
            # Generate recommendations based on insights
            recommendations = self._generate_group_recommendations(analysis)
            
            result = {
                "analysis": analysis,
                "group_metrics": metrics,
                "recommendations": recommendations
            }
            
            # Cache the result
            await cache.set(cache_key, result, self.cache_ttl)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in analyze_group_dynamics: {str(e)}", exc_info=True)
            raise

    def _calculate_engagement_score(self, student_data: Dict[str, Any], classroom_data: Dict[str, Any]) -> float:
        """Calculate student engagement score based on various metrics."""
        try:
            # Calculate participation component
            participation_score = student_data['attendance_rate'] * 0.3
            
            # Calculate homework completion component
            homework_scores = [lesson['score'] for lesson in student_data['lesson_history']]
            homework_score = np.mean(homework_scores) / 100 * 0.3 if homework_scores else 0
            
            # Calculate attention span component
            attention_score = min(1.0, len(student_data['lesson_history']) / 10) * 0.2
            
            # Calculate interaction component
            interaction_score = classroom_data['participation_rate'] * 0.2
            
            # Combine scores
            engagement_score = participation_score + homework_score + attention_score + interaction_score
            
            return min(1.0, engagement_score)
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {str(e)}", exc_info=True)
            return 0.5  # Default score if calculation fails

    def _calculate_group_metrics(self, group_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate key metrics for group analysis."""
        try:
            # Calculate diversity score based on learning styles and performance levels
            learning_styles = len(group_data['composition']['diversity_metrics']['learning_styles'])
            performance_levels = len(group_data['composition']['diversity_metrics']['performance_levels'])
            diversity_score = min(1.0, (learning_styles + performance_levels) / 6.0)  # Normalize to 0-1
            
            # Calculate interaction score based on collaboration metrics
            collaboration_levels = {
                "high": 1.0,
                "medium": 0.7,
                "low": 0.4
            }
            interaction_score = collaboration_levels.get(
                group_data['interaction_patterns']['collaboration_level'].lower(),
                0.5
            )
            
            # Calculate performance score
            performance_score = group_data['learning_outcomes']['average_performance'] / 100.0
            
            # Calculate overall score with weighted components
            overall_score = (
                0.3 * diversity_score +
                0.3 * interaction_score +
                0.4 * performance_score
            )
            
            return {
                "diversity_score": diversity_score,
                "interaction_score": interaction_score,
                "performance_score": performance_score,
                "overall_score": overall_score
            }
            
        except Exception as e:
            logger.error(f"Error in _calculate_group_metrics: {str(e)}", exc_info=True)
            return {
                "diversity_score": 0.5,
                "interaction_score": 0.5,
                "performance_score": 0.5,
                "overall_score": 0.5
            }

    def _generate_group_recommendations(self, analysis: str) -> List[Dict[str, Any]]:
        """Generate structured recommendations from analysis."""
        try:
            # Split analysis into sections
            sections = analysis.split('\n\n')
            recommendations = []
            
            for section in sections:
                if section.strip():
                    recommendations.append({
                        "area": "group_dynamics",
                        "recommendation": section.strip(),
                        "implementation": [
                            f"Step 1: {section.split(':')[0]} strategy",
                            "Step 2: Monitor progress",
                            "Step 3: Adjust as needed",
                            "Step 4: Review and refine"
                        ]
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in _generate_group_recommendations: {str(e)}", exc_info=True)
            return []

    def _generate_performance_prompt(self, student_data: Dict[str, Any], prediction: float) -> str:
        """Generate prompt for performance analysis."""
        return f"""Analyze the following student performance data:

Student Information:
- ID: {student_data['student_id']}
- Grade: {student_data['grade']}
- Subjects: {', '.join(student_data['subjects'])}
- Attendance Rate: {student_data['attendance_rate']*100}%

Previous Grades:
{json.dumps(student_data['previous_grades'], indent=2)}

Lesson History:
{json.dumps(student_data['lesson_history'], indent=2)}

Predicted Performance Score: {prediction:.2f}

Please provide:
1. Performance analysis
2. Strengths and areas for improvement
3. Learning style insights
4. Specific recommendations for improvement
5. Actionable next steps

Format the response in a clear, structured manner with specific examples."""

    def _generate_recommendations(self, ai_response: str) -> List[Dict[str, Any]]:
        """Generate structured recommendations from AI response."""
        try:
            # Split response into sections
            sections = ai_response.split('\n\n')
            recommendations = []
            
            for section in sections:
                if section.strip():
                    recommendations.append({
                        "area": "performance",
                        "recommendation": section.strip(),
                        "implementation": [
                            f"Step 1: {section.split(':')[0]} strategy",
                            "Step 2: Monitor progress",
                            "Step 3: Adjust as needed",
                            "Step 4: Review and refine"
                        ]
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
            return []

    def _prepare_features(self, student_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for performance prediction."""
        try:
            # Extract relevant features
            features = [
                student_data['grade'],
                student_data['attendance_rate'],
                np.mean([lesson['score'] for lesson in student_data['lesson_history']]) if student_data['lesson_history'] else 0,
                len(student_data['lesson_history'])
            ]
            
            # Scale features
            features_scaled = self.scaler.fit_transform(np.array(features).reshape(1, -1))
            
            return features_scaled
            
        except Exception as e:
            logger.error(f"Error preparing features: {str(e)}", exc_info=True)
            raise

    def _load_models(self):
        """Load ML models."""
        try:
            # Create models directory if it doesn't exist
            os.makedirs(settings.MODEL_PATH, exist_ok=True)
            
            # Initialize models as None
            self.performance_model = None
            self.behavior_model = None
            self.audio_model = None
            
            # Try to load performance prediction model
            performance_model_path = os.path.join(settings.MODEL_PATH, "performance_prediction.h5")
            if os.path.exists(performance_model_path):
                self.performance_model = tf.keras.models.load_model(performance_model_path)
                logger.info("Loaded performance prediction model")
            else:
                logger.warning(f"Performance prediction model not found at {performance_model_path}")
            
            # Try to load behavior analysis model
            behavior_model_path = os.path.join(settings.MODEL_PATH, "behavior_analysis.joblib")
            if os.path.exists(behavior_model_path):
                self.behavior_model = joblib.load(behavior_model_path)
                logger.info("Loaded behavior analysis model")
            else:
                logger.warning(f"Behavior analysis model not found at {behavior_model_path}")
            
            # Try to load audio analysis model
            audio_model_path = os.path.join(settings.MODEL_PATH, "audio_analysis.h5")
            if os.path.exists(audio_model_path):
                self.audio_model = tf.keras.models.load_model(audio_model_path)
                logger.info("Loaded audio analysis model")
            else:
                logger.warning(f"Audio analysis model not found at {audio_model_path}")
            
            # Initialize vision models
            self.mp_pose = mp.solutions.pose
            self.mp_face_mesh = mp.solutions.face_mesh
            self.pose = self.mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,
                min_detection_confidence=0.5
            )
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                min_detection_confidence=0.5
            )
            
            logger.info("ML models initialization completed")
        except Exception as e:
            logger.error(f"Error loading ML models: {str(e)}", exc_info=True)
            # Initialize models as None in case of error
            self.performance_model = None
            self.behavior_model = None
            self.audio_model = None
            self.pose = None
            self.face_mesh = None

@lru_cache()
def get_ai_analytics_service() -> AIAnalytics:
    """Get cached AI analytics service instance."""
    return AIAnalytics() 