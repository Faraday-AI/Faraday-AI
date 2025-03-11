from google.cloud import translate_v2 as translate
import logging
from functools import lru_cache
import os
from typing import Dict, Any
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.settings = get_settings()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.settings.GOOGLE_CREDENTIALS_FILE
        self.client = translate.Client()

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
            result = self.client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )

            return {
                "status": "success",
                "translated_text": result["translatedText"],
                "source_language": result["detectedSourceLanguage"],
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
            result = self.client.detect_language(text)
            return {
                "status": "success",
                "language": result["language"],
                "confidence": result["confidence"]
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
    return TranslationService() 