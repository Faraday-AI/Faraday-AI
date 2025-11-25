"""
Optimized AI Service for Jasper
Implements all 7 optimization strategies for maximum speed and efficiency.
"""

import logging
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from openai import OpenAI
from app.core.prompt_cache import get_cached_intent, cache_intent

logger = logging.getLogger(__name__)


class OptimizedAIService:
    """
    Ultra-optimized AI service implementing:
    1. Prompt token reduction
    2. JSON schema response format
    3. Two-model pipeline (mini for intent, full for main)
    4. Parallelization
    5. Caching
    6. Streaming
    7. DB query optimization
    """
    
    def __init__(self, openai_client: OpenAI, mini_model: str = "gpt-4o-mini", main_model: str = "gpt-4"):
        self.openai_client = openai_client
        self.mini_model = mini_model
        self.main_model = main_model
    
    async def classify_intent_fast(self, user_message: str, previous_asked_allergies: bool = False) -> str:
        """
        Ultra-fast intent classification using mini model.
        Uses caching to avoid repeated API calls.
        
        Returns: 'meal_plan', 'workout', 'lesson_plan', 'widget', 'allergy_answer', or 'general'
        """
        # Check cache first
        cache_key = f"{user_message}:{previous_asked_allergies}"
        cached = get_cached_intent(cache_key)
        if cached:
            return cached
        
        # Use mini model for fast classification
        classification_prompt = f"""Classify this user message into ONE of these intents:
- meal_plan: meal plan, nutrition, diet, food plan, calories, macros
- workout: workout, exercise, training, fitness plan, strength training
- lesson_plan: lesson plan, teach, unit plan, curriculum, teaching plan
- widget: attendance, teams, analytics, widget, capabilities, features
- allergy_answer: allergy, allergic, food restriction, intolerance, avoid
- general: anything else

Message: "{user_message}"

Respond with ONLY the intent name (e.g., "meal_plan"):"""
        
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.mini_model,
                messages=[{"role": "user", "content": classification_prompt}],
                temperature=0.1,
                max_tokens=20
            )
            
            intent = response.choices[0].message.content.strip().lower()
            # Normalize intent
            if "meal" in intent or "nutrition" in intent:
                intent = "meal_plan"
            elif "workout" in intent or "exercise" in intent:
                intent = "workout"
            elif "lesson" in intent:
                intent = "lesson_plan"
            elif "widget" in intent or "attendance" in intent:
                intent = "widget"
            elif "allergy" in intent:
                intent = "allergy_answer"
            else:
                intent = "general"
            
            # Cache result
            cache_intent(cache_key, intent)
            logger.info(f"⚡ Fast intent classification: {intent} (using {self.mini_model})")
            return intent
            
        except Exception as e:
            logger.error(f"❌ Error in fast intent classification: {e}")
            # Fallback to keyword-based classification
            from app.core.prompt_loader import classify_intent
            return classify_intent(user_message, previous_asked_allergies)
    
    async def generate_response_streaming(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Generate response with streaming for faster first-token latency.
        
        Returns:
            Tuple of (full_response_text, usage_metadata)
        """
        model = model or self.main_model
        
        # Build request parameters
        request_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        
        if max_tokens:
            request_params["max_tokens"] = max_tokens
        
        if response_format:
            request_params["response_format"] = response_format
        
        # Stream response
        full_response = ""
        usage_metadata = {}
        
        try:
            stream = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                **request_params
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                
                # Capture usage if available
                if hasattr(chunk, 'usage') and chunk.usage:
                    usage_metadata = {
                        "prompt_tokens": chunk.usage.prompt_tokens or 0,
                        "completion_tokens": chunk.usage.completion_tokens or 0,
                        "total_tokens": chunk.usage.total_tokens or 0
                    }
            
            logger.info(f"⚡ Streaming response complete: {len(full_response)} chars")
            return full_response, usage_metadata
            
        except Exception as e:
            logger.error(f"❌ Streaming error: {e}")
            # Fallback to non-streaming
            return await self.generate_response_non_streaming(
                messages, model, temperature, max_tokens, response_format
            )
    
    async def generate_response_non_streaming(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Generate response without streaming (fallback).
        """
        model = model or self.main_model
        
        request_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            request_params["max_tokens"] = max_tokens
        
        if response_format:
            request_params["response_format"] = response_format
        
        response = await asyncio.to_thread(
            self.openai_client.chat.completions.create,
            **request_params
        )
        
        full_response = response.choices[0].message.content
        usage_metadata = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
        
        return full_response, usage_metadata
    
    def get_json_schema_for_widget(self, widget_type: str) -> Optional[Dict]:
        """
        Get JSON schema for structured widget output.
        Reduces parsing overhead and ensures consistent format.
        """
        schemas = {
            "meal_plan": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "day": {"type": "integer"},
                                "meals": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "meal_type": {"type": "string"},
                                            "foods": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "name": {"type": "string"},
                                                        "serving_size": {"type": "string"},
                                                        "calories": {"type": "integer"}
                                                    },
                                                    "required": ["name", "serving_size", "calories"]
                                                }
                                            }
                                        },
                                        "required": ["meal_type", "foods"]
                                    }
                                },
                                "daily_totals": {
                                    "type": "object",
                                    "properties": {
                                        "calories": {"type": "integer"},
                                        "protein": {"type": "number"},
                                        "carbs": {"type": "number"},
                                        "fat": {"type": "number"}
                                    }
                                }
                            },
                            "required": ["day", "meals"]
                        }
                    }
                },
                "required": ["days"]
            },
            "workout": {
                "type": "object",
                "properties": {
                    "exercises": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "sets": {"type": "integer"},
                                "reps": {"type": "string"},
                                "weight": {"type": "string"},
                                "rest": {"type": "string"},
                                "muscle_groups": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["name", "sets", "reps"]
                        }
                    }
                },
                "required": ["exercises"]
            },
            "lesson_plan": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "objectives": {"type": "array", "items": {"type": "string"}},
                    "materials": {"type": "array", "items": {"type": "string"}},
                    "activities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "duration": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["title", "description", "objectives"]
            }
        }
        
        return schemas.get(widget_type)
    
    async def generate_parallel_responses(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[Any]:
        """
        Generate multiple responses in parallel using asyncio.gather.
        
        Args:
            tasks: List of task dicts with keys: messages, model, temperature, max_tokens, response_format
        
        Returns:
            List of (response_text, usage_metadata) tuples
        """
        async def generate_one(task: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
            use_streaming = task.get("stream", False)
            if use_streaming:
                return await self.generate_response_streaming(
                    task["messages"],
                    task.get("model"),
                    task.get("temperature", 0.7),
                    task.get("max_tokens"),
                    task.get("response_format")
                )
            else:
                return await self.generate_response_non_streaming(
                    task["messages"],
                    task.get("model"),
                    task.get("temperature", 0.7),
                    task.get("max_tokens"),
                    task.get("response_format")
                )
        
        # Run all tasks in parallel
        results = await asyncio.gather(*[generate_one(task) for task in tasks])
        logger.info(f"⚡ Parallel generation complete: {len(results)} responses")
        return results

