"""
Text-to-Speech API Endpoints

Provides endpoints for generating voice samples using Azure Cognitive Services.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Header
from fastapi.responses import StreamingResponse
from typing import Optional, Union
import logging
import jwt
from io import BytesIO

from app.services.azure.azure_tts_service import get_azure_tts_service
from app.dashboard.dependencies.auth import get_current_user, JWT_SECRET, JWT_ALGORITHM

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/text-to-speech", tags=["Text-to-Speech"])


async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """Optional authentication - returns None for guest users instead of raising 401."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        # Extract token and decode manually to avoid raising 401
        token = authorization.split(" ", 1)[1] if " " in authorization else None
        if not token:
            return None
        
        # Try to decode token manually
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id:
                return {"id": user_id}
        except (jwt.ExpiredSignatureError, jwt.PyJWTError):
            # Token invalid or expired - allow guest access
            return None
    except Exception:
        # Any error - allow guest access
        return None
    return None


@router.post("/synthesize")
async def synthesize_speech(
    text: str = Query(..., description="Text to synthesize"),
    voice_name: Optional[str] = Query(None, description="Azure voice name (e.g., en-US-JennyNeural)"),
    language: Optional[str] = Query(None, description="Language code (e.g., en-US)"),
    rate: Optional[float] = Query(None, ge=0.2, le=2.0, description="Speech rate (0.2 to 2.0)"),
    pitch: Optional[float] = Query(None, ge=-50, le=50, description="Pitch adjustment (-50 to +50 semitones)"),
    volume: Optional[float] = Query(None, ge=0.0, le=1.0, description="Volume (0.0 to 1.0)"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Synthesize speech from text using Azure TTS.
    
    Returns audio data in WAV format.
    """
    try:
        tts_service = get_azure_tts_service()
        
        if not tts_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Azure TTS service is not configured. Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables."
            )
        
        # Synthesize speech
        audio_data = tts_service.synthesize_speech(
            text=text,
            voice_name=voice_name,
            language=language,
            rate=rate,
            pitch=pitch,
            volume=volume
        )
        
        if audio_data is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to synthesize speech"
            )
        
        # Return audio as streaming response
        audio_data.seek(0)  # Reset to beginning
        return StreamingResponse(
            audio_data,
            media_type="audio/mpeg",  # MP3 format
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error synthesizing speech: {str(e)}"
        )


@router.post("/voice-sample")
async def generate_voice_sample(
    voice_id: str = Query(..., description="Voice ID from the database"),
    text: Optional[str] = Query(
        "Hello, this is a sample of my voice. I can help you with your questions.",
        description="Sample text to speak"
    ),
    rate: Optional[float] = Query(None, ge=0.2, le=2.0, description="Speech rate override (0.2 to 2.0). If provided, overrides database settings."),
    pitch: Optional[float] = Query(None, ge=-50, le=50, description="Pitch adjustment override (-50 to +50 semitones). If provided, overrides database settings."),
    volume: Optional[float] = Query(None, ge=0.0, le=1.0, description="Volume override (0.0 to 1.0). If provided, overrides database settings."),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Generate a voice sample for a specific voice from the database.
    
    Uses voice settings from the database to configure the Azure TTS voice.
    """
    try:
        from app.core.database import SessionLocal
        from sqlalchemy.orm import Session
        from app.models.user_management.avatar.voice import Voice, VoiceTemplate
        from sqlalchemy import text as sql_text
        
        # Get database session
        db = SessionLocal()
        try:
            logger.info(f"Processing voice-sample request: voice_id={voice_id}, text_length={len(text) if text else 0}")
            
            # Get voice from database using the same query method as beta voices service
            voice_row = None
            template_row = None
            
            try:
                # Try to get voice by ID using raw SQL (same as beta voices service)
                voice_id_int = int(voice_id) if voice_id.isdigit() else None
                if voice_id_int:
                    logger.info(f"Querying voices table for id={voice_id_int} using raw SQL")
                    query = sql_text("""
                        SELECT 
                            v.id,
                            v.voice_type,
                            v.voice_settings,
                            v.voice_metadata,
                            vt.id as template_id,
                            vt.name as template_name,
                            vt.description as template_description,
                            vt.voice_settings as template_settings,
                            vt.template_metadata
                        FROM voices v
                        LEFT JOIN voice_templates vt ON v.template_id = vt.id
                        WHERE v.id = :voice_id
                        LIMIT 1
                    """)
                    result = db.execute(query, {'voice_id': voice_id_int})
                    voice_row = result.fetchone()
                    logger.info(f"Voice query result: {voice_row is not None}")
                else:
                    # Try template ID
                    if voice_id.startswith("template_"):
                        template_id = int(voice_id.replace("template_", ""))
                        logger.info(f"Querying voice_templates table for id={template_id} using raw SQL")
                        query = sql_text("""
                            SELECT 
                                id,
                                name,
                                description,
                                voice_settings,
                                template_metadata
                            FROM voice_templates
                            WHERE id = :template_id
                            LIMIT 1
                        """)
                        result = db.execute(query, {'template_id': template_id})
                        template_row = result.fetchone()
                        logger.info(f"Template query result: {template_row is not None}")
                    else:
                        logger.warning(f"voice_id '{voice_id}' is not a valid integer or template ID")
            except Exception as e:
                logger.error(f"Error querying voice for voice_id={voice_id}: {str(e)}", exc_info=True)
            
            # Convert row data to dict-like structure for compatibility
            voice = None
            template = None
            if voice_row:
                # Create a simple object to hold the row data
                class VoiceRow:
                    def __init__(self, row):
                        self.id = row.id
                        self.voice_type = row.voice_type
                        self.voice_settings = row.voice_settings
                        self.voice_metadata = row.voice_metadata
                        self.template_id = row.template_id
                voice = VoiceRow(voice_row)
            elif template_row:
                # Create a simple object to hold the template row data
                class TemplateRow:
                    def __init__(self, row):
                        self.id = row.id
                        self.name = getattr(row, 'name', None)
                        self.description = getattr(row, 'description', None)
                        self.voice_settings = getattr(row, 'voice_settings', None)
                        self.template_metadata = getattr(row, 'template_metadata', None)
                template = TemplateRow(template_row)
            
            # Get voice settings from row data
            settings = {}
            metadata = {}
            language = None
            voice_name = None
            
            if voice_row:
                # Extract settings and metadata from voice row
                try:
                    voice_settings_raw = voice_row.voice_settings
                    if isinstance(voice_settings_raw, dict):
                        settings = voice_settings_raw
                    elif isinstance(voice_settings_raw, str):
                        import json
                        settings = json.loads(voice_settings_raw)
                    else:
                        settings = {}
                except Exception as e:
                    logger.warning(f"Error parsing voice_settings: {e}")
                    settings = {}
                
                try:
                    voice_metadata_raw = voice_row.voice_metadata
                    if isinstance(voice_metadata_raw, dict):
                        metadata = voice_metadata_raw
                    elif isinstance(voice_metadata_raw, str):
                        import json
                        metadata = json.loads(voice_metadata_raw)
                    else:
                        metadata = {}
                except Exception as e:
                    logger.warning(f"Error parsing voice_metadata: {e}")
                    metadata = {}
                
                # Get language and voice_name from metadata
                language = metadata.get('language') or metadata.get('locale')
                voice_name = metadata.get('voice_name') or metadata.get('name')
                
                # Also check template metadata if available
                if voice_row.template_metadata:
                    try:
                        template_metadata = voice_row.template_metadata
                        if isinstance(template_metadata, str):
                            import json
                            template_metadata = json.loads(template_metadata)
                        if isinstance(template_metadata, dict):
                            if not language:
                                language = template_metadata.get('language') or template_metadata.get('locale')
                            if not voice_name:
                                voice_name = template_metadata.get('voice_name') or template_metadata.get('name')
                    except Exception as e:
                        logger.warning(f"Error parsing template_metadata: {e}")
            
            elif template_row:
                # Extract settings and metadata from template row
                try:
                    template_settings_raw = template_row.voice_settings
                    if isinstance(template_settings_raw, dict):
                        settings = template_settings_raw
                    elif isinstance(template_settings_raw, str):
                        import json
                        settings = json.loads(template_settings_raw)
                    else:
                        settings = {}
                except Exception as e:
                    logger.warning(f"Error parsing template voice_settings: {e}")
                    settings = {}
                
                try:
                    template_metadata_raw = template_row.template_metadata
                    if isinstance(template_metadata_raw, dict):
                        metadata = template_metadata_raw
                    elif isinstance(template_metadata_raw, str):
                        import json
                        metadata = json.loads(template_metadata_raw)
                    else:
                        metadata = {}
                except Exception as e:
                    logger.warning(f"Error parsing template_metadata: {e}")
                    metadata = {}
                
                # Get language and voice_name from metadata
                language = metadata.get('language') or metadata.get('locale') if isinstance(metadata, dict) else None
                voice_name = metadata.get('voice_name') or metadata.get('name') if isinstance(metadata, dict) else None
            
            # Extract settings - ensure settings is a dict
            if not isinstance(settings, dict):
                settings = {}
            # Get rate/pitch/volume from database settings (will be overridden by query params if provided)
            db_rate = settings.get('speed') if settings else None
            db_pitch = settings.get('pitch') if settings else None
            db_volume = settings.get('volume') if settings else None
            
            # Get TTS service
            tts_service = get_azure_tts_service()
            
            if not tts_service.is_available():
                raise HTTPException(
                    status_code=503,
                    detail="Azure TTS service is not configured. Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables."
                )
            
            # Map voice name to Azure voice if needed
            # The database voice_name might be generic, so we need to map it to actual Azure voice names
            azure_voice_name = None
            
            # Get the actual database voice ID for mapping
            db_voice_id = None
            if voice_row:
                db_voice_id = voice_row.id
            elif template_row:
                db_voice_id = template_row.id
            
            # Fallback to parameter voice_id if database ID not available
            if db_voice_id is None:
                try:
                    db_voice_id = int(voice_id) if str(voice_id).isdigit() else None
                except:
                    pass
            
            # If still no ID, use hash of voice_id string
            if db_voice_id is None:
                db_voice_id = hash(str(voice_id)) % 1000
            
            # First, try to get Azure voice name directly from metadata
            # Ensure metadata is a dict before accessing it
            if metadata and isinstance(metadata, dict):
                azure_voice_name = metadata.get('azure_voice_name') or metadata.get('azure_voice')
            else:
                azure_voice_name = None
            
            # If not found, try to map from voice_name or use language
            if not azure_voice_name:
                # Use database voice ID to select different voices so each voice sounds unique
                voice_id_num = int(db_voice_id) if db_voice_id else (int(voice_id) if str(voice_id).isdigit() else hash(str(voice_id)) % 1000)
                
                # Use the same premium voices list as beta_teacher_dashboard_service for consistency
                premium_voices = [
                    "en-US-AriaNeural", "en-US-JennyNeural", "en-US-MichelleNeural", "en-US-AshleyNeural",
                    "en-US-AmberNeural", "en-US-AnaNeural", "en-US-AriaMultilingualNeural",
                    "en-US-ChristopherNeural", "en-US-EricNeural", "en-US-GuyNeural", "en-US-RogerNeural",
                    "en-US-DavisNeural", "en-US-JasonNeural", "en-US-BrandonNeural", "en-US-TonyNeural",
                    "en-GB-SoniaNeural", "en-GB-LibbyNeural", "en-GB-MaisieNeural", "en-GB-RyanNeural",
                    "en-GB-ThomasNeural", "en-AU-NatashaNeural", "en-AU-WilliamNeural",
                    "en-CA-ClaraNeural", "en-CA-LiamNeural", "en-IN-NeerjaNeural", "en-IN-PrabhatNeural",
                    "en-IE-EmilyNeural", "en-IE-ConnorNeural", "en-NZ-MollyNeural", "en-NZ-MitchellNeural",
                    "en-ZA-LeahNeural", "en-ZA-LukeNeural",
                    "es-ES-ElviraNeural", "es-ES-AlvaroNeural", "es-MX-DaliaNeural", "es-MX-JorgeNeural",
                    "es-AR-ElenaNeural", "es-AR-TomasNeural", "fr-FR-DeniseNeural", "fr-FR-HenriNeural",
                    "fr-CA-SylvieNeural", "fr-CA-JeanNeural", "de-DE-KatjaNeural", "de-DE-ConradNeural",
                    "de-AT-IngridNeural", "de-CH-JanNeural", "it-IT-ElsaNeural", "it-IT-IsabellaNeural",
                    "it-IT-DiegoNeural", "pt-BR-FranciscaNeural", "pt-BR-AntonioNeural",
                    "pt-PT-RaquelNeural", "pt-PT-DuarteNeural", "ja-JP-NanamiNeural", "ja-JP-KeitaNeural",
                    "zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "zh-CN-XiaoyiNeural",
                    "zh-HK-HiuGaaiNeural", "zh-TW-HsiaoYuNeural", "ko-KR-SunHiNeural", "ko-KR-InJoonNeural",
                    "nl-NL-FennaNeural", "nl-NL-MaartenNeural", "ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural",
                    "ar-SA-ZariyahNeural", "ar-SA-HamedNeural", "hi-IN-SwaraNeural", "hi-IN-MadhurNeural",
                ]
                
                # Select voice based on voice_id to ensure consistency with display names
                azure_voice_name = premium_voices[voice_id_num % len(premium_voices)]
                
                logger.info(f"Mapped voice_id={voice_id} (db_voice_id={db_voice_id}, voice_id_num={voice_id_num}) to Azure voice: {azure_voice_name}")
                
                # If we have language info and it doesn't match the selected voice, try to use a voice for that language
                if language and language != "en-US":
                    # Extract locale from selected voice
                    selected_locale = azure_voice_name.split('-')[0] + '-' + azure_voice_name.split('-')[1] if '-' in azure_voice_name else "en-US"
                    if selected_locale != language:
                        neural_voice_map = {
                            "en-GB": ["en-GB-SoniaNeural", "en-GB-RyanNeural", "en-GB-LibbyNeural", "en-GB-MaisieNeural"],
                            "es-ES": ["es-ES-ElviraNeural", "es-ES-AlvaroNeural", "es-ES-MarinaNeural"],
                            "fr-FR": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural", "fr-FR-BrigitteNeural"],
                            "de-DE": ["de-DE-KatjaNeural", "de-DE-ConradNeural", "de-DE-AmalaNeural"],
                            "it-IT": ["it-IT-ElsaNeural", "it-IT-IsabellaNeural", "it-IT-DiegoNeural"],
                            "pt-BR": ["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural", "pt-BR-ThalitaNeural"],
                            "ja-JP": ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural", "ja-JP-AoiNeural"],
                            "zh-CN": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunyangNeural", "zh-CN-YunxiNeural"],
                            "ko-KR": ["ko-KR-SunHiNeural", "ko-KR-InJoonNeural", "ko-KR-BongJinNeural"]
                        }
                        if language in neural_voice_map:
                            lang_voices = neural_voice_map[language]
                            azure_voice_name = lang_voices[voice_id_num % len(lang_voices)]
                            logger.info(f"Switched to language-specific voice: {azure_voice_name} for language: {language}")
            
            # If still no voice, use language to select default
            if not azure_voice_name:
                if language:
                    # Expanded language map with multiple voice options per language
                    neural_voice_map = {
                        "en-US": ["en-US-AriaNeural", "en-US-JennyNeural", "en-US-MichelleNeural", "en-US-AshleyNeural", "en-US-ChristopherNeural", "en-US-GuyNeural", "en-US-EricNeural"],
                        "en-GB": ["en-GB-SoniaNeural", "en-GB-LibbyNeural", "en-GB-RyanNeural", "en-GB-ThomasNeural"],
                        "en-AU": ["en-AU-NatashaNeural", "en-AU-WilliamNeural"],
                        "en-CA": ["en-CA-ClaraNeural", "en-CA-LiamNeural"],
                        "en-IN": ["en-IN-NeerjaNeural", "en-IN-PrabhatNeural"],
                        "es-ES": ["es-ES-ElviraNeural", "es-ES-AlvaroNeural"],
                        "es-MX": ["es-MX-DaliaNeural", "es-MX-JorgeNeural"],
                        "fr-FR": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"],
                        "fr-CA": ["fr-CA-SylvieNeural", "fr-CA-JeanNeural"],
                        "de-DE": ["de-DE-KatjaNeural", "de-DE-ConradNeural"],
                        "it-IT": ["it-IT-ElsaNeural", "it-IT-IsabellaNeural", "it-IT-DiegoNeural"],
                        "pt-BR": ["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural"],
                        "pt-PT": ["pt-PT-RaquelNeural", "pt-PT-DuarteNeural"],
                        "ja-JP": ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural"],
                        "zh-CN": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "zh-CN-XiaoyiNeural"],
                        "ko-KR": ["ko-KR-SunHiNeural", "ko-KR-InJoonNeural"],
                        "nl-NL": ["nl-NL-FennaNeural", "nl-NL-MaartenNeural"],
                        "ru-RU": ["ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural"],
                        "ar-SA": ["ar-SA-ZariyahNeural", "ar-SA-HamedNeural"],
                        "hi-IN": ["hi-IN-SwaraNeural", "hi-IN-MadhurNeural"],
                    }
                    lang_voices = neural_voice_map.get(language, ["en-US-AriaNeural"])
                    # Use voice_id to select from available voices for this language
                    voice_idx = (int(db_voice_id) if db_voice_id else hash(str(voice_id)) % 1000) % len(lang_voices)
                    azure_voice_name = lang_voices[voice_idx]
                else:
                    # Use voice_id to select from a diverse pool of high-quality neural voices
                    voice_id_num = int(db_voice_id) if db_voice_id else hash(str(voice_id)) % 1000
                    
                    # Comprehensive list of premium neural voices with diverse accents and styles
                    premium_voices = [
                        # US English - Diverse, realistic voices
                        "en-US-AriaNeural",      # Female, warm, professional
                        "en-US-JennyNeural",     # Female, friendly, conversational
                        "en-US-MichelleNeural",  # Female, clear, articulate
                        "en-US-AshleyNeural",    # Female, expressive
                        "en-US-AmberNeural",     # Female, warm
                        "en-US-AnaNeural",       # Female, young
                        "en-US-AriaMultilingualNeural",  # Multilingual female
                        "en-US-ChristopherNeural", # Male, professional
                        "en-US-EricNeural",      # Male, friendly
                        "en-US-GuyNeural",       # Male, clear, confident
                        "en-US-RogerNeural",     # Male, warm
                        "en-US-DavisNeural",     # Male, expressive
                        "en-US-JasonNeural",     # Male, conversational
                        "en-US-BrandonNeural",   # Male, professional
                        "en-US-TonyNeural",      # Male, friendly
                        
                        # British English - Various accents
                        "en-GB-SoniaNeural",     # Female, RP accent
                        "en-GB-LibbyNeural",     # Female, warm
                        "en-GB-MaisieNeural",    # Female, young
                        "en-GB-RyanNeural",      # Male, RP accent
                        "en-GB-ThomasNeural",    # Male, clear
                        
                        # Australian English
                        "en-AU-NatashaNeural",   # Female, Australian accent
                        "en-AU-WilliamNeural",   # Male, Australian accent
                        
                        # Canadian English
                        "en-CA-ClaraNeural",     # Female, Canadian accent
                        "en-CA-LiamNeural",      # Male, Canadian accent
                        
                        # Indian English
                        "en-IN-NeerjaNeural",    # Female, Indian accent
                        "en-IN-PrabhatNeural",   # Male, Indian accent
                        
                        # Irish English
                        "en-IE-EmilyNeural",     # Female, Irish accent
                        "en-IE-ConnorNeural",   # Male, Irish accent
                        
                        # New Zealand English
                        "en-NZ-MollyNeural",     # Female, NZ accent
                        "en-NZ-MitchellNeural", # Male, NZ accent
                        
                        # South African English
                        "en-ZA-LeahNeural",      # Female, SA accent
                        "en-ZA-LukeNeural",      # Male, SA accent
                        
                        # Spanish - Multiple countries
                        "es-ES-ElviraNeural",    # Female, Spain
                        "es-ES-AlvaroNeural",    # Male, Spain
                        "es-MX-DaliaNeural",     # Female, Mexico
                        "es-MX-JorgeNeural",    # Male, Mexico
                        "es-AR-ElenaNeural",    # Female, Argentina
                        "es-AR-TomasNeural",    # Male, Argentina
                        
                        # French
                        "fr-FR-DeniseNeural",    # Female, France
                        "fr-FR-HenriNeural",     # Male, France
                        "fr-CA-SylvieNeural",    # Female, Canada
                        "fr-CA-JeanNeural",      # Male, Canada
                        
                        # German
                        "de-DE-KatjaNeural",     # Female, Germany
                        "de-DE-ConradNeural",    # Male, Germany
                        "de-AT-IngridNeural",   # Female, Austria
                        "de-CH-JanNeural",       # Male, Switzerland
                        
                        # Italian
                        "it-IT-ElsaNeural",      # Female, Italy
                        "it-IT-IsabellaNeural",  # Female, expressive
                        "it-IT-DiegoNeural",     # Male, Italy
                        
                        # Portuguese
                        "pt-BR-FranciscaNeural", # Female, Brazil
                        "pt-BR-AntonioNeural",   # Male, Brazil
                        "pt-PT-RaquelNeural",   # Female, Portugal
                        "pt-PT-DuarteNeural",    # Male, Portugal
                        
                        # Japanese
                        "ja-JP-NanamiNeural",    # Female, Japan
                        "ja-JP-KeitaNeural",     # Male, Japan
                        
                        # Chinese
                        "zh-CN-XiaoxiaoNeural",  # Female, Mandarin
                        "zh-CN-YunxiNeural",     # Male, Mandarin
                        "zh-CN-XiaoyiNeural",    # Female, young
                        "zh-HK-HiuGaaiNeural",   # Female, Cantonese
                        "zh-TW-HsiaoYuNeural",   # Female, Taiwan
                        
                        # Korean
                        "ko-KR-SunHiNeural",     # Female, Korea
                        "ko-KR-InJoonNeural",    # Male, Korea
                        
                        # Other languages
                        "nl-NL-FennaNeural",     # Female, Dutch
                        "nl-NL-MaartenNeural",   # Male, Dutch
                        "ru-RU-SvetlanaNeural",  # Female, Russian
                        "ru-RU-DmitryNeural",    # Male, Russian
                        "ar-SA-ZariyahNeural",   # Female, Arabic
                        "ar-SA-HamedNeural",     # Male, Arabic
                        "hi-IN-SwaraNeural",      # Female, Hindi
                        "hi-IN-MadhurNeural",     # Male, Hindi
                    ]
                    azure_voice_name = premium_voices[voice_id_num % len(premium_voices)]
            
            # Use user-provided rate/pitch/volume from query params if available, otherwise use database settings
            # Query params take precedence over database settings
            final_rate = rate if rate is not None else (db_rate if db_rate is not None else 1.0)
            final_pitch = pitch if pitch is not None else (db_pitch if db_pitch is not None else 0.0)
            final_volume = volume if volume is not None else (db_volume if db_volume is not None else 0.8)
            
            logger.info(f"Voice settings - Query params: rate={rate}, pitch={pitch}, volume={volume} | DB settings: rate={db_rate}, pitch={db_pitch}, volume={db_volume} | Final: rate={final_rate}, pitch={final_pitch}, volume={final_volume}")
            logger.info(f"Using Azure voice: {azure_voice_name} for voice_id: {voice_id} (db_voice_id: {db_voice_id}, language: {language}, voice_name: {voice_name})")
            
            # Synthesize speech
            try:
                audio_data = tts_service.synthesize_speech(
                    text=text,
                    voice_name=azure_voice_name,
                    language=language,
                    rate=final_rate,
                    pitch=final_pitch,
                    volume=final_volume
                )
                
                if audio_data is None:
                    sample_text_preview = str(text)[:50] if text else "None"
                    logger.error(f"TTS service returned None for voice: {azure_voice_name}, text: {sample_text_preview}...")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to synthesize speech - service returned no audio data"
                    )
            except Exception as tts_error:
                logger.error(f"Error in TTS synthesis: {str(tts_error)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to synthesize speech: {str(tts_error)}"
                )
            
            # Return audio as streaming response with error handling for connection closures
            audio_data.seek(0)
            
            # Create a generator that handles connection errors gracefully
            def generate_audio():
                try:
                    while True:
                        chunk = audio_data.read(8192)  # Read in 8KB chunks
                        if not chunk:
                            break
                        yield chunk
                except Exception as e:
                    # Connection closed or error during streaming - log but don't raise
                    logger.warning(f"Connection closed during audio streaming: {str(e)}")
                    # Don't raise - just stop generating chunks
            
            return StreamingResponse(
                generate_audio(),
                media_type="audio/mpeg",  # MP3 format for faster download
                headers={
                    "Content-Disposition": "inline; filename=voice_sample.mp3",
                    "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
                }
            )
        finally:
            db.close()
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error generating voice sample for voice_id={voice_id}: {error_msg}", exc_info=True)
        # Provide more detailed error message
        import traceback
        tb_str = traceback.format_exc()
        logger.error(f"Full traceback: {tb_str}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating voice sample: {error_msg}"
        )


@router.get("/voices")
async def get_available_voices(
    language: Optional[str] = Query(None, description="Filter by language code"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    Get list of available Azure TTS voices.
    """
    try:
        tts_service = get_azure_tts_service()
        
        if not tts_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Azure TTS service is not configured"
            )
        
        voices = tts_service.get_available_voices(language=language)
        return {"voices": voices}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting available voices: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting available voices: {str(e)}"
        )

