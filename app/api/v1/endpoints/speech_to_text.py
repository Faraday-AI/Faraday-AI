"""
Speech-to-text endpoint for Safari compatibility.
Safari doesn't support Web Speech API, so we use getUserMedia + backend transcription.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from typing import Optional
import logging
import io
from openai import OpenAI
from app.core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_optional_user(
    authorization: Optional[str] = Header(None)
):
    """Get current user if token is provided, otherwise return None."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        token = authorization.replace("Bearer ", "")
        # Try to get user, but don't fail if token is invalid
        # This allows guest users to use speech-to-text
        from app.core.auth import get_user_from_token
        return get_user_from_token(token)
    except:
        return None

@router.post("/speech-to-text")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: Optional[str] = "en",
    current_user: Optional[dict] = Depends(get_optional_user)
) -> JSONResponse:
    """
    Transcribe audio to text using OpenAI Whisper API.
    This endpoint is used for Safari compatibility since Safari doesn't support Web Speech API.
    
    Args:
        audio: Audio file (webm, wav, mp3, etc.)
        language: Language code (default: "en")
        
    Returns:
        JSON with transcribed text
    """
    try:
        settings = get_settings()
        
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured"
            )
        
        # Read audio data
        audio_data = await audio.read()
        
        if not audio_data:
            raise HTTPException(
                status_code=400,
                detail="No audio data received"
            )
        
        # Check if audio data is empty
        if len(audio_data) < 1:
            raise HTTPException(
                status_code=400,
                detail="No audio data received"
            )
        
        # Log warning for very small files but still try to process
        if len(audio_data) < 100:
            logger.warning(f"Audio file is very small: {len(audio_data)} bytes - may not contain actual audio")
        
        # If the file is too small, provide a helpful message before trying Whisper
        if len(audio_data) < 100:
            error_msg = f"Audio file too small ({len(audio_data)} bytes). Safari's MediaRecorder may not be capturing audio properly. Please try using Chrome or Firefox for voice input."
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )
        
        # Initialize OpenAI client
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Prepare audio file for Whisper API
        audio_file = io.BytesIO(audio_data)
        
        # Determine file extension from content type or filename
        filename = audio.filename or "audio.webm"
        content_type = audio.content_type or ""
        
        # Ensure proper file extension for Whisper
        # Whisper supports: mp3, mp4, mpeg, mpga, m4a, wav, webm
        if filename.endswith(('.webm', '.mp3', '.wav', '.m4a', '.mp4', '.mpeg', '.mpga')):
            audio_file.name = filename
        elif 'webm' in content_type.lower() or 'webm' in filename.lower():
            audio_file.name = "audio.webm"
        elif 'mp3' in content_type.lower() or 'mp3' in filename.lower():
            audio_file.name = "audio.mp3"
        elif 'wav' in content_type.lower() or 'wav' in filename.lower():
            audio_file.name = "audio.wav"
        else:
            # Default to webm for Safari MediaRecorder
            audio_file.name = "audio.webm"
        
        logger.info(f"Transcribing audio file: {len(audio_data)} bytes, filename: {audio_file.name}, content_type: {content_type}, original_filename: {filename}")
        
        # Transcribe using Whisper
        try:
            logger.info(f"Calling Whisper API with file size: {len(audio_data)} bytes, format: {audio_file.name}")
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
            transcribed_text = transcript.text if hasattr(transcript, 'text') else str(transcript)
            logger.info(f"Whisper API success: {len(transcribed_text)} characters transcribed: '{transcribed_text[:200]}...'")
            
            # Log first few bytes of audio for debugging
            logger.debug(f"Audio file first 100 bytes (hex): {audio_data[:100].hex()}")
        except Exception as whisper_error:
            error_msg = str(whisper_error) if whisper_error else "Unknown error"
            error_type = type(whisper_error).__name__
            logger.error(f"Whisper API error ({error_type}): {error_msg}")
            logger.error(f"Whisper error details: {repr(whisper_error)}")
            
            # Extract more details if it's an OpenAI API error
            if hasattr(whisper_error, 'response'):
                try:
                    if hasattr(whisper_error.response, 'json'):
                        error_data = whisper_error.response.json()
                        if 'error' in error_data and 'message' in error_data['error']:
                            error_msg = error_data['error']['message']
                            logger.error(f"Extracted error message from response: {error_msg}")
                except Exception as parse_error:
                    logger.warning(f"Could not parse error response: {parse_error}")
            
            # Provide helpful message for small files
            if len(audio_data) < 1000:
                error_msg = f"Invalid audio file ({len(audio_data)} bytes). Safari's MediaRecorder may not be capturing audio properly. Please try using Chrome or Firefox for voice input. Original error: {error_msg}"
            
            raise HTTPException(
                status_code=500,
                detail=f"Whisper API error: {error_msg}"
            )
        
        transcribed_text = transcript.text if hasattr(transcript, 'text') else str(transcript)
        
        # Log if transcription seems incomplete (very short for a longer recording)
        if len(transcribed_text) < 10 and len(audio_data) > 10000:
            logger.warning(f"⚠️ Transcription seems incomplete: only '{transcribed_text}' transcribed from {len(audio_data)} bytes of audio")
        
        return JSONResponse({
            "text": transcribed_text,
            "language": language,
            "status": "success"
        })
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions as-is
        raise http_exc
    except Exception as e:
        error_msg = str(e) if e else "Unknown error"
        error_type = type(e).__name__
        logger.error(f"Unexpected error transcribing audio ({error_type}): {error_msg}")
        logger.error(f"Error details: {repr(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=500,
            detail=f"Error transcribing audio: {error_msg}"
        )

