from openai import OpenAI, OpenAIError
from typing import Optional, Dict, Any
import logging
from functools import lru_cache
import backoff
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY)

    @backoff.on_exception(
        backoff.expo,
        (OpenAIError, Exception),
        max_tries=3,
        max_time=30
    )
    async def generate_text(self, prompt: str, structured_output: bool = False) -> Dict[str, Any]:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7 if not structured_output else 0.2,
                max_tokens=2000,
                response_format={"type": "json_object"} if structured_output else None
            )
            return {
                "content": response.choices[0].message.content,
                "status": "success"
            }
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return {
                "content": None,
                "status": "error",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error in generate_text: {str(e)}")
            return {
                "content": None,
                "status": "error",
                "error": "An unexpected error occurred"
            }

@lru_cache()
def get_openai_service() -> OpenAIService:
    """Get cached OpenAI service instance."""
    return OpenAIService() 