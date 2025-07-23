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
import pandas as pd
from pathlib import Path
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.layers import Input, LSTM, Dense
from tensorflow.keras.metrics import AUC, Precision, Recall

logger = logging.getLogger(__name__)
settings = get_settings()
metrics = MetricsCollector()
cache = Cache()

# Rate limiting configuration
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds

class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, requests_per_window: int, window_seconds: int):
        """Initialize rate limiter."""
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests = {}  # client_id -> list of timestamps
        
    def is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited."""
        now = time.time()
        if client_id not in self.requests:
            self.requests[client_id] = []
            
        # Remove old requests
        self.requests[client_id] = [t for t in self.requests[client_id] 
                                  if now - t < self.window_seconds]
        
        # Check if rate limited
        if len(self.requests[client_id]) >= self.requests_per_window:
            return True
            
        # Add new request
        self.requests[client_id].append(now)
        return False
        
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        now = time.time()
        if client_id not in self.requests:
            return self.requests_per_window
            
        # Remove old requests
        self.requests[client_id] = [t for t in self.requests[client_id] 
                                  if now - t < self.window_seconds]
        
        return self.requests_per_window - len(self.requests[client_id])

rate_limiter = RateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW)

class PhysicalEducationAI:
    """AI service specifically designed for Physical Education assistance."""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.GPT_MODEL
        self._init_pe_prompts()
        self._init_ml_models()

    def _init_ml_models(self):
        """Initialize ML models for analysis"""
        try:
            # Initialize models directory - use local path instead of Docker path
            base_dir = Path(__file__).parent.parent.parent
            self.models_dir = base_dir / "models"
            self.models_dir.mkdir(parents=True, exist_ok=True)
            
            # Load or create movement analysis model
            movement_model_path = self.models_dir / "movement_analysis_model.keras"
            logger.info(f"Loading movement model from: {movement_model_path}")
            
            if movement_model_path.exists():
                self.movement_model = load_model(str(movement_model_path))
            else:
                logger.info("Model file not found, creating new model")
                # Create model with Input layer
                inputs = Input(shape=(None, 17))  # 17 keypoints with x,y coordinates
                x = LSTM(64, return_sequences=True)(inputs)
                x = LSTM(32)(x)
                x = Dense(16, activation='relu')(x)
                outputs = Dense(1, activation='sigmoid')(x)
                self.movement_model = Model(inputs=inputs, outputs=outputs)
                
                # Compile model with metrics
                self.movement_model.compile(
                    optimizer='adam',
                    loss='binary_crossentropy',
                    metrics=['accuracy', AUC(), Precision(), Recall()]
                )
                
                # Save the model
                self.movement_model.save(str(movement_model_path), save_format='keras')
                logger.info(f"Model saved to: {movement_model_path}")
            
            logger.info("Movement model loaded successfully")
            
            # Load adaptation model
            adaptation_model_path = self.models_dir / "activity_adaptation.joblib"
            logger.info(f"Loading adaptation model from: {adaptation_model_path}")
            self.adaptation_model = joblib.load(str(adaptation_model_path))
            logger.info("Adaptation model loaded successfully")
            
            # Load assessment model
            assessment_model_path = self.models_dir / "skill_assessment.joblib"
            logger.info(f"Loading assessment model from: {assessment_model_path}")
            self.assessment_model = joblib.load(str(assessment_model_path))
            logger.info("Assessment model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ML models: {str(e)}")
            raise

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
    """AI Analytics service for educational data analysis."""
    
    def __init__(self):
        """Initialize AI Analytics service."""
        # Define models directory
        self.models_dir = Path("/app/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Define model paths
        self.model_paths = {
            'performance': self.models_dir / 'performance_prediction.joblib',
            'behavior': self.models_dir / 'behavior_analysis.joblib',
            'audio': self.models_dir / 'audio_analysis.keras'
        }
        
        # Initialize models as None
        self.models = {name: None for name in self.model_paths.keys()}
        
        # Try to load models
        self._load_models()
    
    def _load_models(self):
        """Load AI models if they exist."""
        for name, path in self.model_paths.items():
            if not path.exists():
                logger.warning(f"{name.title()} model not found at {path}")
                continue
            
            try:
                if path.suffix in ['.h5', '.keras']:
                    # Load TensorFlow model
                    self.models[name] = tf.keras.models.load_model(str(path))
                elif path.suffix == '.joblib':
                    # Load scikit-learn model
                    self.models[name] = joblib.load(str(path))
                logger.info(f"Successfully loaded {name} model from {path}")
            except Exception as e:
                logger.error(f"Error loading {name} model: {str(e)}")
    
    def analyze_performance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze student performance data."""
        if self.models['performance'] is None:
            return {"status": "unavailable", "message": "Performance prediction model not available"}
        try:
            # Process data and make predictions
            result = {"status": "success", "predictions": {}}
            return result
        except Exception as e:
            logger.error(f"Error in performance analysis: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def analyze_behavior(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze student behavior data."""
        if self.models['behavior'] is None:
            return {"status": "unavailable", "message": "Behavior analysis model not available"}
        try:
            # Process data and make predictions
            result = {"status": "success", "analysis": {}}
            return result
        except Exception as e:
            logger.error(f"Error in behavior analysis: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def analyze_audio(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audio data."""
        if self.models['audio'] is None:
            return {"status": "unavailable", "message": "Audio analysis model not available"}
        try:
            # Process audio data and make predictions
            result = {"status": "success", "analysis": {}}
            return result
        except Exception as e:
            logger.error(f"Error in audio analysis: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def cleanup(self):
        """Cleanup resources."""
        # Clear models from memory
        self.models = {name: None for name in self.models.keys()}

@lru_cache()
def get_ai_analytics_service() -> AIAnalytics:
    """Get cached AI analytics service instance."""
    return AIAnalytics() 