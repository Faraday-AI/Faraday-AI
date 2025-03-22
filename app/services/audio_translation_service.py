from typing import Dict, Optional
import openai
from app.core.config import get_settings
import logging
import asyncio
import aiohttp
import io
import wave
import numpy as np

logger = logging.getLogger(__name__)

class AudioTranslationService:
    def __init__(self):
        self.settings = get_settings()
        openai.api_key = self.settings.OPENAI_API_KEY

    async def translate_audio(self, audio_data: bytes, source_lang: str, target_lang: str) -> Dict:
        """
        Translate audio from one language to another in real-time.
        
        Args:
            audio_data: Raw audio data
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Dict containing translation results
        """
        try:
            # First, transcribe the audio using Whisper
            transcription = await self._transcribe_audio(audio_data)
            
            # Then translate the transcription
            translation = await self._translate_text(
                transcription["text"],
                source_lang,
                target_lang
            )
            
            return {
                "transcription": transcription["text"],
                "translation": translation["text"],
                "confidence": transcription["confidence"],
                "language": transcription["language"]
            }
            
        except Exception as e:
            logger.error(f"Error in audio translation: {str(e)}")
            raise

    async def _transcribe_audio(self, audio_data: bytes) -> Dict:
        """Transcribe audio using OpenAI's Whisper API."""
        try:
            # Convert audio data to the correct format if needed
            audio_file = self._prepare_audio(audio_data)
            
            response = await openai.Audio.transcribe(
                "whisper-1",
                audio_file,
                language="en"  # Can be made configurable
            )
            
            return {
                "text": response["text"],
                "confidence": response.get("confidence", 0.0),
                "language": response.get("language", "en")
            }
            
        except Exception as e:
            logger.error(f"Error in audio transcription: {str(e)}")
            raise

    async def _translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """Translate text using OpenAI's API."""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a translator. Translate from {source_lang} to {target_lang}."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3
            )
            
            return {
                "text": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Error in text translation: {str(e)}")
            raise

    def _prepare_audio(self, audio_data: bytes) -> io.BytesIO:
        """Prepare audio data for the Whisper API."""
        # Convert audio data to the correct format if needed
        # This is a simplified version - you might need more sophisticated audio processing
        audio_file = io.BytesIO(audio_data)
        return audio_file

    async def stream_translation(self, audio_stream, source_lang: str, target_lang: str):
        """
        Stream audio translation in real-time.
        
        Args:
            audio_stream: Async iterator yielding audio chunks
            source_lang: Source language code
            target_lang: Target language code
            
        Yields:
            Dict containing translation results for each chunk
        """
        try:
            async for chunk in audio_stream:
                result = await self.translate_audio(chunk, source_lang, target_lang)
                yield result
                
        except Exception as e:
            logger.error(f"Error in streaming translation: {str(e)}")
            raise

    async def translate_audio_file(self, file_path: str, source_lang: str, target_lang: str) -> Dict:
        """
        Translate an audio file from one language to another.
        
        Args:
            file_path: Path to the audio file
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Dict containing translation results
        """
        try:
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            
            return await self.translate_audio(audio_data, source_lang, target_lang)
            
        except Exception as e:
            logger.error(f"Error in audio file translation: {str(e)}")
            raise 
