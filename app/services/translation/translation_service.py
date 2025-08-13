import logging
from functools import lru_cache
import os
from typing import Dict, Any, Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class MockTranslationService:
    """Mock translation service when Google Cloud is not available."""
    async def translate_text(
        self,
        text: str,
        target_language: str = "es",
        source_language: str = "en"
    ) -> Dict[str, Any]:
        return {
            "status": "success",
            "translated_text": text,  # Return original text
            "source_language": source_language,
            "target_language": target_language,
            "note": "Translation service is not configured"
        }

    async def detect_language(self, text: str) -> Dict[str, Any]:
        return {
            "status": "success",
            "language": "en",
            "confidence": 1.0,
            "note": "Language detection is not configured"
        }

class TranslationService:
    def __init__(self):
        self.settings = get_settings()
        if not self.settings.ENABLE_GOOGLE_CLOUD:
            raise ValueError("Google Cloud services are not enabled")
        
        credentials_file = getattr(self.settings, 'GOOGLE_CREDENTIALS_FILE', None)
        if not credentials_file:
            raise ValueError("Google Cloud credentials not configured")
        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file
        
        try:
            from google.cloud import translate
            self.client = translate.TranslationServiceClient()
        except ImportError:
            raise ValueError("Google Cloud Translation library not installed")

    async def translate_text(
        self,
        text: str,
        target_language: str = "es",
        source_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Translate text using Google Cloud Translation API.
        
        Args:
            text: Text to translate
            target_language: Target language code (default: es for Spanish)
            source_language: Source language code (default: en for English)
            
        Returns:
            Dict containing translated text and detection info
        """
        try:
            result = self.client.translate_text(
                request={
                    "contents": [text],
                    "target_language_code": target_language,
                    "source_language_code": source_language,
                }
            )

            return {
                "status": "success",
                "translated_text": result.translations[0].translated_text,
                "source_language": result.translations[0].detected_language_code,
                "target_language": target_language
            }

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of the input text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict containing detected language info
        """
        try:
            result = self.client.detect_language(
                request={
                    "contents": [text],
                }
            )
            return {
                "status": "success",
                "language": result.languages[0].language_code,
                "confidence": result.languages[0].confidence
            }
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

@lru_cache()
def get_translation_service() -> TranslationService:
    """Get cached Translation service instance."""
    try:
        return TranslationService()
    except (ValueError, ImportError) as e:
        logger.warning(f"Using mock translation service: {str(e)}")
        return MockTranslationService() 