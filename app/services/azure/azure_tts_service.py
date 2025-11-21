"""
Azure Text-to-Speech Service

This service provides text-to-speech functionality using Azure Cognitive Services Speech REST API.
Uses REST API instead of SDK for better cross-platform compatibility (especially ARM64).
"""

from typing import Optional, Dict, Any, BinaryIO
import logging
from io import BytesIO
import requests
import time
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AzureTTSService:
    """Azure Text-to-Speech service using Cognitive Services Speech REST API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.speech_key = self.settings.AZURE_SPEECH_KEY
        self.speech_region = self.settings.AZURE_SPEECH_REGION
        
        if not self.speech_key or not self.speech_region:
            logger.warning("Azure Speech credentials not configured. TTS will not be available.")
            self._access_token = None
            self._token_expiry = 0
        else:
            self._access_token = None
            self._token_expiry = 0
            # Base URLs for REST API
            self._token_url = f"https://{self.speech_region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
            self._tts_url = f"https://{self.speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"
            logger.info(f"Azure TTS service initialized for region: {self.speech_region} (REST API)")
    
    def _get_access_token(self) -> Optional[str]:
        """
        Get or refresh Azure Speech access token.
        Tokens are valid for 10 minutes, so we cache them.
        """
        # Check if we have a valid cached token
        if self._access_token and time.time() < self._token_expiry:
            return self._access_token
        
        try:
            headers = {
                "Ocp-Apim-Subscription-Key": self.speech_key,
                "Content-Length": "0"
            }
            response = requests.post(self._token_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            self._access_token = response.text
            # Cache token for 9 minutes (tokens are valid for 10 minutes)
            self._token_expiry = time.time() + (9 * 60)
            logger.debug("Azure Speech access token obtained")
            return self._access_token
        except Exception as e:
            logger.error(f"Failed to obtain Azure Speech access token: {str(e)}")
            return None
    
    def is_available(self) -> bool:
        """Check if Azure TTS service is available."""
        return self.speech_key is not None and self.speech_region is not None
    
    def synthesize_speech(
        self,
        text: str,
        voice_name: Optional[str] = None,
        language: Optional[str] = None,
        rate: Optional[float] = None,
        pitch: Optional[float] = None,
        volume: Optional[float] = None,
        style: Optional[str] = None
    ) -> Optional[BytesIO]:
        """
        Synthesize speech from text using Azure TTS REST API.
        
        Args:
            text: Text to synthesize
            voice_name: Name of the voice to use (e.g., "en-US-JennyNeural")
            language: Language code (e.g., "en-US")
            rate: Speech rate (0.2 to 2.0, default 1.0)
            pitch: Pitch adjustment (-50 to +50 semitones, default 0)
            volume: Volume (0.0 to 1.0, default 1.0)
            
        Returns:
            BytesIO object containing audio data (WAV format), or None if synthesis fails
        """
        if not self.is_available():
            logger.error("Azure TTS service is not available")
            return None
        
        try:
            # Get access token
            access_token = self._get_access_token()
            if not access_token:
                logger.error("Failed to obtain Azure Speech access token")
                return None
            
            # Determine the voice name to use
            resolved_voice_name = None
            if voice_name:
                resolved_voice_name = voice_name
            elif language:
                # Try to find a neural voice for the language
                neural_voices = {
                    "en-US": "en-US-JennyNeural",
                    "en-GB": "en-GB-SoniaNeural",
                    "es-ES": "es-ES-ElviraNeural",
                    "fr-FR": "fr-FR-DeniseNeural",
                    "de-DE": "de-DE-KatjaNeural",
                    "it-IT": "it-IT-ElsaNeural",
                    "pt-BR": "pt-BR-FranciscaNeural",
                    "ja-JP": "ja-JP-NanamiNeural",
                    "zh-CN": "zh-CN-XiaoxiaoNeural",
                    "ko-KR": "ko-KR-SunHiNeural"
                }
                if language in neural_voices:
                    resolved_voice_name = neural_voices[language]
            
            # Default voice if none specified
            if not resolved_voice_name:
                resolved_voice_name = "en-US-JennyNeural"
            
            logger.info(f"Using Azure voice: {resolved_voice_name} for synthesis (language: {language}, rate: {rate})")
            
            # Create SSML for advanced voice control
            ssml_text = self._create_ssml(text, resolved_voice_name, rate, pitch, volume, style)
            
            # Make REST API request
            # Use MP3 format for faster download (much smaller than WAV)
            # audio-16khz-128kbitrate-mono-mp3 is good quality and fast
            # For even faster: audio-16khz-64kbitrate-mono-mp3 or audio-16khz-32kbitrate-mono-mp3
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-16khz-64kbitrate-mono-mp3",  # MP3 format - much faster than WAV
                "User-Agent": "Faraday-AI-TTS"
            }
            
            # Calculate timeout based on text length
            # Azure TTS typically processes ~100-200 characters per second
            # For longer texts (like lesson plans), we need more time
            # Base timeout: 30 seconds, add 1 second per 100 characters over 2000
            text_length = len(text)
            if text_length > 2000:
                # For long texts (lesson plans), allow more time
                # 30 seconds base + 1 second per 100 chars over 2000
                timeout = 30 + ((text_length - 2000) // 100)
                # Cap at 120 seconds (2 minutes) for very long texts
                timeout = min(timeout, 120)
            else:
                timeout = 30
            
            logger.info(f"Azure TTS request: {text_length} characters, timeout: {timeout}s")
            
            response = requests.post(
                self._tts_url,
                headers=headers,
                data=ssml_text.encode('utf-8'),
                timeout=timeout
            )
            
            response.raise_for_status()
            
            # Return audio data
            return BytesIO(response.content)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error synthesizing speech (HTTP error): {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}, body: {e.response.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}", exc_info=True)
            return None
    
    def _create_ssml(
        self,
        text: str,
        voice_name: str,
        rate: Optional[float] = None,
        pitch: Optional[float] = None,
        volume: Optional[float] = None,
        style: Optional[str] = None
    ) -> str:
        """
        Create SSML markup for speech synthesis with voice parameters and optional style.
        
        Args:
            text: Text to synthesize (will be XML-escaped)
            voice_name: Azure voice name
            rate: Speech rate (0.5 to 2.0)
            pitch: Pitch adjustment in semitones (-50 to +50)
            volume: Volume (0.0 to 1.0)
            style: Optional voice style
        """
        import xml.sax.saxutils
        
        # Escape XML special characters in text
        # This handles &, <, >, ', and " characters
        escaped_text = xml.sax.saxutils.escape(text)
        # Default values
        rate_value = rate if rate is not None else 1.0
        pitch_value = pitch if pitch is not None else 0.0
        volume_value = volume if volume is not None else 1.0
        
        # Clamp values to valid ranges (Azure TTS supports 20% to 200%, which is 0.2 to 2.0 rate)
        rate_value = max(0.2, min(2.0, rate_value))
        pitch_value = max(-50, min(50, pitch_value))
        volume_value = max(0.0, min(1.0, volume_value))
        
        # Convert rate to percentage (Azure uses percentage)
        rate_percent = int(rate_value * 100)
        
        # Convert volume to percentage
        volume_percent = int(volume_value * 100)
        
        # Convert pitch to integer (Azure expects integer semitones)
        pitch_int = int(round(pitch_value))
        
        # Extract language from voice name (e.g., "en-US-JennyNeural" -> "en-US")
        # Default to en-US if we can't extract it
        lang = "en-US"
        if voice_name and '-' in voice_name:
            parts = voice_name.split('-')
            if len(parts) >= 2:
                lang = f"{parts[0]}-{parts[1]}"
        
        # Valid Azure voice styles (some voices support these)
        valid_styles = [
            "cheerful", "sad", "angry", "fearful", "disgruntled", "serious", 
            "affectionate", "gentle", "lyrical", "embarrassed", "calm", 
            "worried", "excited", "friendly", "hopeful", "unfriendly", "terrified"
        ]
        
        # Use style if provided and valid
        style_attr = ""
        if style and style.lower() in valid_styles:
            style_attr = f" style='{style.lower()}'"
        
        # Create SSML with explicit voice name and optional style
        # Use escaped_text instead of raw text to prevent XML parsing errors
        if style_attr:
            ssml = f"""<speak version='1.0' xml:lang='{lang}' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='https://www.w3.org/2001/mstts'>
    <voice name='{voice_name}'>
        <mstts:express-as{style_attr}>
            <prosody rate='{rate_percent}%' pitch='{pitch_int:+d}st' volume='{volume_percent}%'>
                {escaped_text}
            </prosody>
        </mstts:express-as>
    </voice>
</speak>"""
        else:
            ssml = f"""<speak version='1.0' xml:lang='{lang}' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='https://www.w3.org/2001/mstts'>
    <voice name='{voice_name}'>
        <prosody rate='{rate_percent}%' pitch='{pitch_int:+d}st' volume='{volume_percent}%'>
            {escaped_text}
        </prosody>
    </voice>
</speak>"""
        
        return ssml
    
    def get_available_voices(self, language: Optional[str] = None) -> list:
        """
        Get list of available voices from Azure using REST API.
        
        Args:
            language: Optional language code to filter voices
            
        Returns:
            List of voice dictionaries
        """
        if not self.is_available():
            return []
        
        try:
            # Get access token
            access_token = self._get_access_token()
            if not access_token:
                logger.error("Failed to obtain Azure Speech access token")
                return []
            
            # Azure REST API endpoint for listing voices
            voices_url = f"https://{self.speech_region}.tts.speech.microsoft.com/cognitiveservices/voices/list"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "Faraday-AI-TTS"
            }
            
            response = requests.get(voices_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            voices_data = response.json()
            voices = []
            
            for voice in voices_data:
                locale = voice.get("Locale", "")
                if language and not locale.startswith(language):
                    continue
                
                voices.append({
                    "name": voice.get("ShortName", ""),
                    "display_name": voice.get("DisplayName", ""),
                    "locale": locale,
                    "gender": voice.get("Gender", ""),
                    "voice_type": "Neural" if "Neural" in voice.get("ShortName", "") else "Standard"
                })
            
            return voices
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting available voices (HTTP error): {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error getting available voices: {str(e)}", exc_info=True)
            return []


# Singleton instance
_azure_tts_service: Optional[AzureTTSService] = None


def get_azure_tts_service() -> AzureTTSService:
    """Get singleton instance of Azure TTS service."""
    global _azure_tts_service
    if _azure_tts_service is None:
        _azure_tts_service = AzureTTSService()
    return _azure_tts_service

