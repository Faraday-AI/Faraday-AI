"""
Beta Teacher Dashboard Service
Handles personal workspace, activity analytics, and dashboard management for beta teachers
This is a separate system from the main teacher dashboard, designed to work independently
without school district or student data.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
import uuid
import json

from app.models.beta_teacher_dashboard import (
    BetaDashboardWidget,
    TeacherDashboardLayout,
    DashboardWidgetInstance,
    TeacherActivityLog,
    TeacherNotification,
    TeacherAchievement,
    TeacherAchievementProgress,
    TeacherQuickAction,
    BetaTeacherPreference,
    TeacherStatistics,
    TeacherGoal,
    TeacherLearningPath,
    LearningPathStep
)
from app.schemas.beta_teacher_dashboard import (
    DashboardConfigResponse,
    BetaDashboardWidgetResponse,
    TeacherDashboardLayoutCreate,
    TeacherDashboardLayoutUpdate,
    TeacherDashboardLayoutResponse,
    BetaDashboardWidgetInstanceCreate,
    BetaDashboardWidgetInstanceUpdate,
    BetaDashboardWidgetInstanceResponse,
    TeacherActivityLogCreate,
    TeacherActivityLogResponse,
    TeacherNotificationResponse,
    TeacherAchievementResponse,
    TeacherAchievementProgressResponse,
    TeacherQuickActionCreate,
    TeacherQuickActionUpdate,
    TeacherQuickActionResponse,
    BetaTeacherPreferenceCreate,
    BetaTeacherPreferenceUpdate,
    BetaTeacherPreferenceResponse,
    TeacherStatisticsResponse,
    TeacherGoalCreate,
    TeacherGoalUpdate,
    TeacherGoalResponse,
    TeacherLearningPathCreate,
    TeacherLearningPathUpdate,
    TeacherLearningPathResponse,
    LearningPathStepCreate,
    LearningPathStepResponse,
    DashboardAnalyticsResponse,
    TeacherDashboardSummaryResponse,
    DashboardLayoutUpdate,
    DashboardPreferencesUpdate,
    BetaDashboardWidgetConfigUpdate,
    DashboardFeedbackResponse
)


class BetaTeacherDashboardService:
    def __init__(self, db: Session):
        self.db = db

    # ==================== DASHBOARD CONFIGURATION (Endpoint Methods) ====================
    
    def get_dashboard(self, teacher_id: str) -> DashboardConfigResponse:
        """Get teacher's dashboard configuration"""
        # Get default layout or create one
        layout = self.get_default_dashboard_layout(teacher_id)
        if not layout:
            # Create default layout if none exists
            default_layout = TeacherDashboardLayoutCreate(
                layout_name="Default Layout",
                layout_description="Default dashboard layout",
                is_default=True
            )
            layout = self.create_dashboard_layout(teacher_id, default_layout)
        
        return DashboardConfigResponse(
            id=str(layout.id),
            teacher_id=teacher_id,
            layout_name=layout.layout_name,
            layout_config={"widgets": [wi.model_dump() for wi in layout.widget_instances]} if hasattr(layout, 'widget_instances') else {},
            is_default=getattr(layout, 'is_default', False),
            is_active=getattr(layout, 'is_active', True),
            created_at=getattr(layout, 'created_at', datetime.utcnow()),
            updated_at=getattr(layout, 'updated_at', datetime.utcnow())
        )
    
    def update_dashboard(self, teacher_id: str, update_data: DashboardLayoutUpdate) -> DashboardConfigResponse:
        """Update teacher's dashboard"""
        layout = self.get_default_dashboard_layout(teacher_id)
        if not layout:
            raise Exception("Dashboard not found")
        
        # Update layout with new data
        layout_data = TeacherDashboardLayoutUpdate(**update_data.dict(exclude_unset=True))
        updated_layout = self.update_dashboard_layout(layout.id, teacher_id, layout_data)
        
        return DashboardConfigResponse(
            id=str(updated_layout.id),
            teacher_id=teacher_id,
            layout_name=updated_layout.layout_name,
            layout_config={"widgets": [wi.model_dump() for wi in updated_layout.widget_instances]} if hasattr(updated_layout, 'widget_instances') else {},
            is_default=getattr(updated_layout, 'is_default', False),
            is_active=getattr(updated_layout, 'is_active', True),
            created_at=getattr(updated_layout, 'created_at', datetime.utcnow()),
            updated_at=getattr(updated_layout, 'updated_at', datetime.utcnow())
        )
    
    def get_dashboard_widgets(self, teacher_id: str, widget_type: Optional[str], is_active: Optional[bool], limit: int, offset: int) -> List[BetaDashboardWidgetResponse]:
        """Get teacher's dashboard widgets"""
        query = self.db.query(BetaDashboardWidget)
        
        if widget_type:
            query = query.filter(BetaDashboardWidget.widget_type == widget_type)
        if is_active is not None:
            query = query.filter(BetaDashboardWidget.is_active == is_active)
        
        widgets = query.order_by(asc(BetaDashboardWidget.created_at)).offset(offset).limit(limit).all()
        return [self._widget_to_response(widget) for widget in widgets]
    
    def get_dashboard_widget(self, widget_id: str, teacher_id: str) -> Optional[BetaDashboardWidgetResponse]:
        """Get specific widget"""
        widget = self.db.query(BetaDashboardWidget).filter(BetaDashboardWidget.id == widget_id).first()
        return self._widget_to_response(widget) if widget else None
    
    def update_dashboard_widget(self, widget_id: str, teacher_id: str, update_data: BetaDashboardWidgetConfigUpdate) -> Optional[BetaDashboardWidgetResponse]:
        """Update widget configuration"""
        widget = self.db.query(BetaDashboardWidget).filter(BetaDashboardWidget.id == widget_id).first()
        if not widget:
            return None
        
        # Update widget fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(widget, field, value)
        
        widget.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._widget_to_response(widget)
    
    def activate_widget(self, widget_id: str, teacher_id: str) -> Optional[BetaDashboardWidgetResponse]:
        """Activate a widget"""
        widget = self.db.query(BetaDashboardWidget).filter(BetaDashboardWidget.id == widget_id).first()
        if not widget:
            return None
        
        widget.is_active = True
        widget.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._widget_to_response(widget)
    
    def deactivate_widget(self, widget_id: str, teacher_id: str) -> Optional[BetaDashboardWidgetResponse]:
        """Deactivate a widget"""
        widget = self.db.query(BetaDashboardWidget).filter(BetaDashboardWidget.id == widget_id).first()
        if not widget:
            return None
        
        widget.is_active = False
        widget.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._widget_to_response(widget)
    
    def get_widget_analytics(self, teacher_id: str, widget_id: Optional[str], days: int) -> Dict[str, Any]:
        """Get widget analytics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(
            TeacherActivityLog.activity_type,
            func.count(TeacherActivityLog.id).label('count')
        ).filter(
            and_(
                TeacherActivityLog.teacher_id == teacher_id,
                TeacherActivityLog.created_at >= start_date
            )
        )
        
        if widget_id:
            query = query.filter(TeacherActivityLog.resource_id == widget_id)
        
        results = query.group_by(TeacherActivityLog.activity_type).all()
        
        return {
            "analytics": {item.activity_type: item.count for item in results},
            "period_days": days,
            "widget_id": widget_id
        }
    
    def submit_dashboard_feedback(self, teacher_id: str, feedback_data: Dict[str, Any]) -> DashboardFeedbackResponse:
        """Submit dashboard feedback"""
        # This is a placeholder implementation
        # In a real system, this would save to a feedback table
        feedback_id = str(uuid.uuid4())
        
        return DashboardFeedbackResponse(
            id=feedback_id,
            teacher_id=teacher_id,
            feedback_type=feedback_data.get("feedback_type", "general"),
            feedback_text=feedback_data.get("feedback_text", ""),
            rating=feedback_data.get("rating"),
            created_at=datetime.utcnow()
        )
    
    def get_dashboard_feedback(self, teacher_id: str, feedback_type: Optional[str], limit: int, offset: int) -> List[DashboardFeedbackResponse]:
        """Get dashboard feedback"""
        # This is a placeholder implementation
        # In a real system, this would query a feedback table
        return []
    
    def get_dashboard_preferences(self, teacher_id: str) -> Dict[str, Any]:
        """Get dashboard preferences"""
        preferences = self.get_teacher_preferences(teacher_id)
        prefs_dict = {}
        for pref in preferences:
            prefs_dict[pref.preference_key] = pref.preference_value
        
        return prefs_dict
    
    def update_dashboard_preferences(self, teacher_id: str, update_data: DashboardPreferencesUpdate) -> Dict[str, Any]:
        """Update dashboard preferences"""
        prefs_dict = update_data.dict(exclude_unset=True)
        
        # Update preferences
        for key, value in prefs_dict.items():
            if key == "preferences" and isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    pref_data = BetaTeacherPreferenceCreate(
                        preference_key=sub_key,
                        preference_value=str(sub_value),
                        preference_type="string"
                    )
                    self.set_teacher_preference(teacher_id, pref_data)
        
        # Get updated preferences
        return self.get_dashboard_preferences(teacher_id)
    
    def get_beta_widgets(self, widget_type: Optional[str], is_active: Optional[bool], limit: int, offset: int) -> List[BetaDashboardWidgetResponse]:
        """Get all beta widgets (330 widgets from beta_widgets table)"""
        # Query beta_widgets table
        from app.models.beta_widgets import BetaWidget
        
        query = self.db.query(BetaWidget)
        
        if widget_type:
            query = query.filter(BetaWidget.widget_type == widget_type)
        if is_active is not None:
            query = query.filter(BetaWidget.is_active == is_active)
        
        widgets = query.offset(offset).limit(limit).all()
        
        # Convert to BetaDashboardWidgetResponse
        result = []
        for widget in widgets:
            widget_name = getattr(widget, 'widget_name', None) or getattr(widget, 'name', 'Unknown Widget')
            widget_description = getattr(widget, 'widget_description', None) or getattr(widget, 'description', '')
            widget_config = getattr(widget, 'widget_config', None) or getattr(widget, 'configuration', {})
            is_system_widget = getattr(widget, 'is_system_widget', False)
            display_order = getattr(widget, 'display_order', 0)
            
            result.append(BetaDashboardWidgetResponse(
                id=str(widget.id) if widget.id else '',
                name=widget_name,
                widget_type=getattr(widget, 'widget_type', ''),
                configuration=widget_config,
                is_active=getattr(widget, 'is_active', True),
                created_at=getattr(widget, 'created_at', datetime.utcnow()),
                updated_at=getattr(widget, 'updated_at', None) or datetime.utcnow()
            ))
        
        return result
    
    def get_beta_avatars(self, voice_enabled: Optional[bool]) -> List[Dict[str, Any]]:
        """Get all beta avatars (10 avatars from beta_avatars table)"""
        from app.models.beta_avatars import BetaAvatar
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # First, check if beta_avatars table exists and has data
            try:
                from sqlalchemy import text
                count_query = text("SELECT COUNT(*) FROM beta_avatars")
                count_result = self.db.execute(count_query)
                total_avatars = count_result.scalar()
                logger.info(f"Total avatars in database: {total_avatars}")
            except Exception as count_error:
                logger.warning(f"Could not count avatars: {str(count_error)}")
                total_avatars = 0
            
            # Query using SQLAlchemy ORM (automatically uses Azure database connection)
            query = self.db.query(BetaAvatar)
            
            if voice_enabled is not None:
                query = query.filter(BetaAvatar.voice_enabled == voice_enabled)
            
            avatars = query.all()
            logger.info(f"Found {len(avatars)} avatars from database query (total in DB: {total_avatars})")
            
            # Generate user-friendly names based on type and index
            avatar_names = {
                'STATIC': ['Classic Avatar', 'Professional Avatar', 'Friendly Avatar', 'Modern Avatar'],
                'ANIMATED': ['Animated Assistant', 'Dynamic Avatar', 'Interactive Avatar', 'Live Avatar'],
                'THREE_D': ['3D Character', '3D Assistant', '3D Avatar', '3D Model']
            }
            
            type_counts = {}
            result = []
            
            for avatar in avatars:
                avatar_type = getattr(avatar, 'type', 'STATIC')
                type_key = avatar_type.upper() if isinstance(avatar_type, str) else str(avatar_type)
                
                # Count how many of this type we've seen
                type_counts[type_key] = type_counts.get(type_key, 0) + 1
                index = type_counts[type_key] - 1
                
                # Get name from predefined list or generate one
                name_list = avatar_names.get(type_key, [f'{type_key} Avatar'])
                if index < len(name_list):
                    avatar_name = name_list[index]
                else:
                    avatar_name = f'{type_key} Avatar {index + 1}'
                
                # Generate description
                descriptions = {
                    'STATIC': 'A static image avatar perfect for professional settings',
                    'ANIMATED': 'An animated avatar with smooth movements and expressions',
                    'THREE_D': 'A 3D model avatar with full rotation and interaction'
                }
                description = descriptions.get(type_key, f'A {type_key.lower()} avatar')
                
                result.append({
                    "id": str(avatar.id),
                    "avatar_name": avatar_name,
                    "avatar_type": avatar_type,
                    "description": description,
                    "voice_enabled": getattr(avatar, 'voice_enabled', False),
                    "image_url": getattr(avatar, 'image_url', None),
                    "avatar_config": getattr(avatar, 'avatar_config', getattr(avatar, 'config', {})),
                    "created_at": avatar.created_at.isoformat() if avatar.created_at else None
                })
            
            if len(result) == 0 and total_avatars > 0:
                logger.warning(f"⚠️ Query returned 0 avatars, but database has {total_avatars} avatars")
            elif len(result) > 0:
                logger.info(f"✅ Successfully retrieved {len(result)} avatars from Azure database")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error fetching avatars from database: {str(e)}", exc_info=True)
            # Return empty list instead of raising - let frontend handle empty state
            return []
    
    def get_beta_avatar(self, avatar_id: str) -> Optional[Dict[str, Any]]:
        """Get specific beta avatar"""
        from app.models.beta_avatars import BetaAvatar
        
        avatar = self.db.query(BetaAvatar).filter(BetaAvatar.id == avatar_id).first()
        
        if not avatar:
            return None
        
        return {
            "id": str(avatar.id),
            "avatar_name": getattr(avatar, 'avatar_name', getattr(avatar, 'name', getattr(avatar, 'type', 'Unknown Avatar'))),
            "avatar_type": getattr(avatar, 'avatar_type', getattr(avatar, 'type', '')),
            "description": getattr(avatar, 'description', ''),
            "voice_enabled": getattr(avatar, 'voice_enabled', False),
            "avatar_config": getattr(avatar, 'avatar_config', getattr(avatar, 'config', {})),
            "created_at": avatar.created_at.isoformat() if avatar.created_at else None
        }
    
    def _get_voice_display_name(self, voice_id: int, metadata: Dict[str, Any] = None) -> str:
        """
        Generate a descriptive display name for a voice based on its ID and metadata.
        Uses the same mapping logic as the TTS endpoint to ensure consistency.
        """
        if metadata is None:
            metadata = {}
        
        # First, try to use existing metadata/name if it's meaningful
        if metadata.get('name') and 'default' not in metadata.get('name', '').lower() and 'standard' not in metadata.get('name', '').lower():
            return metadata.get('name')
        
        if metadata.get('voice_name') and 'default' not in metadata.get('voice_name', '').lower():
            return metadata.get('voice_name')
        
        # Map voice_id to Azure voice name (same logic as text_to_speech.py)
        voice_id_num = int(voice_id) if voice_id else hash(str(voice_id)) % 1000
        
        # Comprehensive mapping of voice IDs to descriptive names
        # This matches the premium_voices list in text_to_speech.py
        voice_descriptions = {
            # US English voices
            "en-US-AriaNeural": "Aria - Warm Professional (US)",
            "en-US-JennyNeural": "Jenny - Friendly Conversational (US)",
            "en-US-MichelleNeural": "Michelle - Clear Articulate (US)",
            "en-US-AshleyNeural": "Ashley - Expressive (US)",
            "en-US-AmberNeural": "Amber - Warm (US)",
            "en-US-AnaNeural": "Ana - Young (US)",
            "en-US-AriaMultilingualNeural": "Aria - Multilingual (US)",
            "en-US-ChristopherNeural": "Christopher - Professional (US)",
            "en-US-EricNeural": "Eric - Friendly (US)",
            "en-US-GuyNeural": "Guy - Confident (US)",
            "en-US-RogerNeural": "Roger - Warm (US)",
            "en-US-DavisNeural": "Davis - Expressive (US)",
            "en-US-JasonNeural": "Jason - Conversational (US)",
            "en-US-BrandonNeural": "Brandon - Professional (US)",
            "en-US-TonyNeural": "Tony - Friendly (US)",
            
            # British English
            "en-GB-SoniaNeural": "Sonia - British RP Accent",
            "en-GB-LibbyNeural": "Libby - Warm British",
            "en-GB-MaisieNeural": "Maisie - Young British",
            "en-GB-RyanNeural": "Ryan - British RP Accent",
            "en-GB-ThomasNeural": "Thomas - Clear British",
            
            # Australian
            "en-AU-NatashaNeural": "Natasha - Australian Accent",
            "en-AU-WilliamNeural": "William - Australian Accent",
            
            # Canadian
            "en-CA-ClaraNeural": "Clara - Canadian Accent",
            "en-CA-LiamNeural": "Liam - Canadian Accent",
            
            # Indian
            "en-IN-NeerjaNeural": "Neerja - Indian Accent",
            "en-IN-PrabhatNeural": "Prabhat - Indian Accent",
            
            # Irish
            "en-IE-EmilyNeural": "Emily - Irish Accent",
            "en-IE-ConnorNeural": "Connor - Irish Accent",
            
            # New Zealand
            "en-NZ-MollyNeural": "Molly - New Zealand Accent",
            "en-NZ-MitchellNeural": "Mitchell - New Zealand Accent",
            
            # South African
            "en-ZA-LeahNeural": "Leah - South African Accent",
            "en-ZA-LukeNeural": "Luke - South African Accent",
            
            # Spanish
            "es-ES-ElviraNeural": "Elvira - Spanish (Spain)",
            "es-ES-AlvaroNeural": "Alvaro - Spanish (Spain)",
            "es-MX-DaliaNeural": "Dalia - Spanish (Mexico)",
            "es-MX-JorgeNeural": "Jorge - Spanish (Mexico)",
            "es-AR-ElenaNeural": "Elena - Spanish (Argentina)",
            "es-AR-TomasNeural": "Tomas - Spanish (Argentina)",
            
            # French
            "fr-FR-DeniseNeural": "Denise - French",
            "fr-FR-HenriNeural": "Henri - French",
            "fr-CA-SylvieNeural": "Sylvie - French (Canada)",
            "fr-CA-JeanNeural": "Jean - French (Canada)",
            
            # German
            "de-DE-KatjaNeural": "Katja - German",
            "de-DE-ConradNeural": "Conrad - German",
            "de-AT-IngridNeural": "Ingrid - German (Austria)",
            "de-CH-JanNeural": "Jan - German (Switzerland)",
            
            # Italian
            "it-IT-ElsaNeural": "Elsa - Italian",
            "it-IT-IsabellaNeural": "Isabella - Expressive Italian",
            "it-IT-DiegoNeural": "Diego - Italian",
            
            # Portuguese
            "pt-BR-FranciscaNeural": "Francisca - Portuguese (Brazil)",
            "pt-BR-AntonioNeural": "Antonio - Portuguese (Brazil)",
            "pt-PT-RaquelNeural": "Raquel - Portuguese (Portugal)",
            "pt-PT-DuarteNeural": "Duarte - Portuguese (Portugal)",
            
            # Japanese
            "ja-JP-NanamiNeural": "Nanami - Japanese",
            "ja-JP-KeitaNeural": "Keita - Japanese",
            
            # Chinese
            "zh-CN-XiaoxiaoNeural": "Xiaoxiao - Chinese (Mandarin)",
            "zh-CN-YunxiNeural": "Yunxi - Chinese (Mandarin)",
            "zh-CN-XiaoyiNeural": "Xiaoyi - Young Chinese (Mandarin)",
            "zh-HK-HiuGaaiNeural": "HiuGaai - Chinese (Cantonese)",
            "zh-TW-HsiaoYuNeural": "HsiaoYu - Chinese (Taiwan)",
            
            # Korean
            "ko-KR-SunHiNeural": "SunHi - Korean",
            "ko-KR-InJoonNeural": "InJoon - Korean",
            
            # Other languages
            "nl-NL-FennaNeural": "Fenna - Dutch",
            "nl-NL-MaartenNeural": "Maarten - Dutch",
            "ru-RU-SvetlanaNeural": "Svetlana - Russian",
            "ru-RU-DmitryNeural": "Dmitry - Russian",
            "ar-SA-ZariyahNeural": "Zariyah - Arabic",
            "ar-SA-HamedNeural": "Hamed - Arabic",
            "hi-IN-SwaraNeural": "Swara - Hindi",
            "hi-IN-MadhurNeural": "Madhur - Hindi",
        }
        
        # List of premium voices (same as in text_to_speech.py)
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
            # Add more voices from the full list...
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
        
        # Select voice from list
        selected_voice = premium_voices[voice_id_num % len(premium_voices)]
        
        # Get description if available
        if selected_voice in voice_descriptions:
            return voice_descriptions[selected_voice]
        
        # Generate description from voice name
        parts = selected_voice.split('-')
        if len(parts) >= 3:
            locale = parts[0] + '-' + parts[1]  # e.g., "en-US"
            name = parts[2].replace('Neural', '')  # e.g., "Aria"
            
            # Map locales to readable names
            locale_names = {
                "en-US": "US English", "en-GB": "British", "en-AU": "Australian",
                "en-CA": "Canadian", "en-IN": "Indian", "en-IE": "Irish",
                "en-NZ": "New Zealand", "en-ZA": "South African",
                "es-ES": "Spanish (Spain)", "es-MX": "Spanish (Mexico)", "es-AR": "Spanish (Argentina)",
                "fr-FR": "French", "fr-CA": "French (Canada)", "de-DE": "German",
                "de-AT": "German (Austria)", "de-CH": "German (Switzerland)",
                "it-IT": "Italian", "pt-BR": "Portuguese (Brazil)", "pt-PT": "Portuguese (Portugal)",
                "ja-JP": "Japanese", "zh-CN": "Chinese (Mandarin)", "zh-HK": "Chinese (Cantonese)",
                "zh-TW": "Chinese (Taiwan)", "ko-KR": "Korean", "nl-NL": "Dutch",
                "ru-RU": "Russian", "ar-SA": "Arabic", "hi-IN": "Hindi"
            }
            
            locale_display = locale_names.get(locale, locale)
            return f"{name} - {locale_display}"
        
        return f"Voice {voice_id}"
    
    def get_beta_voices(
        self, 
        avatar_id: Optional[str] = None,
        language: Optional[str] = None,
        provider: Optional[str] = None,
        limit: int = 500,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all available voices (320+ voices from voices and voice_templates tables)"""
        from app.models.user_management.avatar.voice import Voice, VoiceTemplate
        from sqlalchemy import text
        
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # First, check if voices table exists and has data
            try:
                count_query = text("SELECT COUNT(*) FROM voices")
                count_result = self.db.execute(count_query)
                total_voices = count_result.scalar()
                logger.info(f"Total voices in database: {total_voices}")
            except Exception as count_error:
                logger.warning(f"Could not count voices: {str(count_error)}")
                total_voices = 0
            
            # Build query dynamically based on filters
            base_query = """
                SELECT 
                    v.id,
                    v.voice_type,
                    v.voice_settings,
                    v.voice_metadata,
                    vt.id as template_id,
                    vt.name as template_name,
                    vt.description as template_description,
                    vt.voice_settings as template_settings
                FROM voices v
                LEFT JOIN voice_templates vt ON v.template_id = vt.id
            """
            
            params = {}
            conditions = []
            
            if avatar_id:
                conditions.append("v.avatar_id = :avatar_id")
                params['avatar_id'] = avatar_id
            
            if language:
                conditions.append("(v.voice_metadata::text LIKE :language OR v.voice_settings::text LIKE :language)")
                params['language'] = f'%{language}%'
            
            if provider:
                conditions.append("(v.voice_metadata::text LIKE :provider)")
                params['provider'] = f'%{provider}%'
            
            # Build final query
            if conditions:
                where_clause = " WHERE " + " AND ".join(conditions)
            else:
                where_clause = ""
            
            query_str = base_query + where_clause + " ORDER BY COALESCE(vt.name, '') NULLS LAST, v.id LIMIT :limit OFFSET :offset"
            params['limit'] = limit
            params['offset'] = offset
            
            logger.info(f"Executing voice query with limit={limit}, offset={offset}, filters={len(conditions)}")
            
            query = text(query_str)
            result = self.db.execute(query, params)
            voices = []
            
            for row in result:
                # Extract metadata for better name generation
                metadata = row.voice_metadata or {}
                if isinstance(metadata, str):
                    try:
                        import json
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                # Build a better name from available data
                name_parts = []
                
                # Check if template name is generic
                template_name = row.template_name or ''
                is_generic_template = template_name.lower() in ['default voice', 'default', 'voice'] or 'default' in template_name.lower()
                
                # Try template name first (if not generic)
                if template_name and not is_generic_template:
                    name_parts.append(template_name)
                # Try metadata name fields
                elif metadata.get('name') and 'default' not in metadata.get('name', '').lower():
                    name_parts.append(metadata.get('name'))
                elif metadata.get('voice_name') and 'default' not in metadata.get('voice_name', '').lower():
                    name_parts.append(metadata.get('voice_name'))
                # Try role or category from metadata
                elif metadata.get('role'):
                    role = metadata.get('role')
                    name_parts.append(f"{role.title()} Voice")
                elif metadata.get('category'):
                    category = metadata.get('category')
                    name_parts.append(f"{category.title()} Voice")
                
                # Add provider if available (skip "system" as it's too generic)
                provider = metadata.get('provider') or metadata.get('service')
                validProvider = provider if provider and provider.lower() != 'system' else ''
                if validProvider:
                    if name_parts:
                        name_parts.append(f"({validProvider})")
                    else:
                        name_parts.append(f"{validProvider.title()} Voice")
                
                # Add language if available
                language = metadata.get('language') or metadata.get('locale')
                if language:
                    if name_parts:
                        name_parts.append(f"- {language}")
                    else:
                        name_parts.append(f"Voice ({language})")
                
                # Try to extract more from settings
                if not name_parts:
                    voice_settings = row.voice_settings or {}
                    if isinstance(voice_settings, str):
                        try:
                            import json
                            voice_settings = json.loads(voice_settings)
                        except:
                            voice_settings = {}
                    
                    # Try gender, accent, or style from settings
                    if voice_settings.get('gender'):
                        name_parts.append(f"{voice_settings.get('gender').title()} Voice")
                    elif voice_settings.get('accent'):
                        name_parts.append(f"{voice_settings.get('accent').title()} Voice")
                    elif voice_settings.get('style'):
                        name_parts.append(f"{voice_settings.get('style').title()} Voice")
                    elif voice_settings.get('name'):
                        name_parts.append(voice_settings.get('name'))
                
                # Fallback to voice type or ID
                if not name_parts:
                    voice_type = row.voice_type or "TTS"
                    # Only use voice type if it's meaningful (not just "TTS" or "system")
                    if voice_type.lower() not in ['tts', 'system', 'default']:
                        name_parts.append(f"{voice_type} Voice")
                    else:
                        # Try to create a name from language/provider if available
                        parts = []
                        if language:
                            parts.append(language)
                        if validProvider:
                            parts.append(validProvider)
                        # Check metadata quality
                        quality = metadata.get('quality', '')
                        if quality and quality != 'high':
                            parts.append(quality)
                        if parts:
                            name_parts.append(f"{' '.join(parts)} Voice")
                        else:
                            # Use the helper function to generate a descriptive name from voice ID
                            descriptive_name = self._get_voice_display_name(row.id, metadata)
                            name_parts.append(descriptive_name)
                
                voice_name = " ".join(name_parts)
                
                voice_data = {
                    "id": str(row.id),
                    "voice_id": str(row.id),
                    "voice_type": row.voice_type or "TTS",
                    "name": voice_name,
                    "description": row.template_description or f"{row.voice_type or 'TTS'} voice",
                    "settings": row.voice_settings or {},
                    "metadata": metadata,
                    "template_id": str(row.template_id) if row.template_id else None,
                    "template_settings": row.template_settings or {}
                }
                voices.append(voice_data)
            
            logger.info(f"Found {len(voices)} voices from database query (total in DB: {total_voices})")
            
            # If we got fewer than limit, also get from voice_templates for more options
            if len(voices) < limit and offset == 0:
                try:
                    template_query = text("""
                        SELECT id, name, description, voice_settings, template_metadata
                        FROM voice_templates
                        ORDER BY name
                        LIMIT :limit
                    """)
                    template_result = self.db.execute(template_query, {'limit': limit - len(voices)})
                    
                    for row in template_result:
                        if not any(v.get('template_id') == str(row.id) for v in voices):
                            voice_data = {
                                "id": f"template_{row.id}",
                                "voice_id": str(row.id),
                                "voice_type": "TTS",
                                "name": row.name or f"Voice Template {row.id}",
                                "description": row.description or "Voice template",
                                "settings": row.voice_settings or {},
                                "metadata": row.template_metadata or {},
                                "template_id": str(row.id),
                                "template_settings": row.voice_settings or {}
                            }
                            voices.append(voice_data)
                except Exception as template_error:
                    # If voice_templates query fails, continue with what we have
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Error fetching voice templates: {str(template_error)}")
            
            # If we still have no voices, try a simpler query
            if len(voices) == 0:
                logger.warning("No voices found with filtered query, trying simple query without filters")
                try:
                    # Try querying without any filters - just get all voices
                    simple_query = text("""
                        SELECT 
                            v.id,
                            v.voice_type,
                            v.voice_settings,
                            v.voice_metadata,
                            vt.id as template_id,
                            vt.name as template_name,
                            vt.description as template_description,
                            vt.voice_settings as template_settings
                        FROM voices v
                        LEFT JOIN voice_templates vt ON v.template_id = vt.id
                        ORDER BY COALESCE(vt.name, '') NULLS LAST, v.id
                        LIMIT :limit
                    """)
                    simple_result = self.db.execute(simple_query, {'limit': limit})
                    voices = []
                    for row in simple_result:
                        # Extract metadata for better name generation
                        metadata = row.voice_metadata or {}
                        if isinstance(metadata, str):
                            try:
                                import json
                                metadata = json.loads(metadata)
                            except:
                                metadata = {}
                        
                        # Build a better name from available data
                        name_parts = []
                        
                        # Check if template name is generic
                        template_name = row.template_name or ''
                        is_generic_template = template_name.lower() in ['default voice', 'default', 'voice'] or 'default' in template_name.lower()
                        
                        # Try template name first (if not generic)
                        if template_name and not is_generic_template:
                            name_parts.append(template_name)
                        # Try metadata name fields
                        elif metadata.get('name') and 'default' not in metadata.get('name', '').lower():
                            name_parts.append(metadata.get('name'))
                        elif metadata.get('voice_name') and 'default' not in metadata.get('voice_name', '').lower():
                            name_parts.append(metadata.get('voice_name'))
                        # Try role or category from metadata
                        elif metadata.get('role'):
                            role = metadata.get('role')
                            name_parts.append(f"{role.title()} Voice")
                        elif metadata.get('category'):
                            category = metadata.get('category')
                            name_parts.append(f"{category.title()} Voice")
                        
                        # Add provider if available (skip "system" as it's too generic)
                        provider = metadata.get('provider') or metadata.get('service')
                        validProvider = provider if provider and provider.lower() != 'system' else ''
                        if validProvider:
                            if name_parts:
                                name_parts.append(f"({validProvider})")
                            else:
                                name_parts.append(f"{validProvider.title()} Voice")
                        
                        # Add language if available
                        language = metadata.get('language') or metadata.get('locale')
                        if language:
                            if name_parts:
                                name_parts.append(f"- {language}")
                            else:
                                name_parts.append(f"Voice ({language})")
                        
                        # Try to extract more from settings
                        if not name_parts:
                            voice_settings = row.voice_settings or {}
                            if isinstance(voice_settings, str):
                                try:
                                    import json
                                    voice_settings = json.loads(voice_settings)
                                except:
                                    voice_settings = {}
                            
                            # Try gender, accent, or style from settings
                            if voice_settings.get('gender'):
                                name_parts.append(f"{voice_settings.get('gender').title()} Voice")
                            elif voice_settings.get('accent'):
                                name_parts.append(f"{voice_settings.get('accent').title()} Voice")
                            elif voice_settings.get('style'):
                                name_parts.append(f"{voice_settings.get('style').title()} Voice")
                            elif voice_settings.get('name'):
                                name_parts.append(voice_settings.get('name'))
                        
                        # Fallback to voice type or ID
                        if not name_parts:
                            voice_type = row.voice_type or "TTS"
                            # Only use voice type if it's meaningful (not just "TTS" or "system")
                            if voice_type.lower() not in ['tts', 'system', 'default']:
                                name_parts.append(f"{voice_type} Voice")
                            else:
                                # Try to create a name from language/provider if available
                                parts = []
                                if language:
                                    parts.append(language)
                                if validProvider:
                                    parts.append(validProvider)
                                # Check metadata quality
                                quality = metadata.get('quality', '')
                                if quality and quality != 'high':
                                    parts.append(quality)
                                if parts:
                                    name_parts.append(f"{' '.join(parts)} Voice")
                                else:
                                    # Use the helper function to generate a descriptive name from voice ID
                                    descriptive_name = self._get_voice_display_name(row.id, metadata)
                                    name_parts.append(descriptive_name)
                        
                        voice_name = " ".join(name_parts)
                        
                        voice_data = {
                            "id": str(row.id),
                            "voice_id": str(row.id),
                            "voice_type": row.voice_type or "TTS",
                            "name": voice_name,
                            "description": row.template_description or f"{row.voice_type or 'TTS'} voice",
                            "settings": row.voice_settings or {},
                            "metadata": metadata,
                            "template_id": str(row.template_id) if row.template_id else None,
                            "template_settings": row.template_settings or {}
                        }
                        voices.append(voice_data)
                    
                    if len(voices) > 0:
                        logger.info(f"✅ Successfully retrieved {len(voices)} voices with simple query (total in DB: {total_voices})")
                        return voices[:limit]
                    else:
                        logger.warning(f"⚠️ Simple query returned 0 voices, but database has {total_voices} voices. Returning fallback.")
                        return self._get_fallback_voices(limit)
                except Exception as simple_error:
                    logger.error(f"❌ Error with simple query: {str(simple_error)}", exc_info=True)
                    logger.warning(f"⚠️ Database has {total_voices} voices but query failed. Returning fallback.")
                    return self._get_fallback_voices(limit)
            
            # Return all voices we found (up to limit)
            logger.info(f"✅ Returning {len(voices)} voices from database")
            return voices[:limit]
            
        except Exception as e:
            # Fallback: return a list of common voices if database query fails
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error fetching voices from database: {str(e)}. Returning default voices.")
            return self._get_fallback_voices(limit)
    
    def _get_fallback_voices(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Generate fallback voices when database is empty or query fails."""
        # Return common TTS voices as fallback
        default_voices = []
        languages = ['en-US', 'en-GB', 'es-ES', 'fr-FR', 'de-DE', 'it-IT', 'pt-BR', 'ja-JP', 'zh-CN', 'ko-KR']
        providers = ['google', 'amazon', 'microsoft', 'elevenlabs']
        voice_names = ['Neural', 'Standard', 'Wavenet', 'Premium']
        
        voice_id = 1
        for provider in providers:
            for language in languages:
                for name in voice_names:
                    if len(default_voices) >= limit:
                        break
                    default_voices.append({
                        "id": f"default_{voice_id}",
                        "voice_id": str(voice_id),
                        "voice_type": "TTS",
                        "name": f"{provider.title()} {name} ({language})",
                        "description": f"{provider.title()} {name} voice for {language}",
                        "settings": {"speed": 1.0, "pitch": 1.0, "volume": 0.8},
                        "metadata": {"provider": provider, "language": language},
                        "template_id": None,
                        "template_settings": {}
                    })
                    voice_id += 1
                if len(default_voices) >= limit:
                    break
            if len(default_voices) >= limit:
                break
        
        return default_voices[:limit]
    
    def reset_dashboard(self, teacher_id: str) -> DashboardConfigResponse:
        """Reset dashboard to default"""
        # Delete all existing layouts for teacher
        self.db.query(TeacherDashboardLayout).filter(
            TeacherDashboardLayout.teacher_id == teacher_id
        ).delete()
        self.db.commit()
        
        # Create new default layout
        return self.get_dashboard(teacher_id)

    # ==================== DASHBOARD LAYOUTS ====================
    
    def create_dashboard_layout(
        self, 
        teacher_id: str, 
        layout_data: TeacherDashboardLayoutCreate
    ) -> TeacherDashboardLayoutResponse:
        """Create a new dashboard layout"""
        try:
            # If this is set as default, unset other defaults
            if layout_data.is_default:
                self.db.query(TeacherDashboardLayout).filter(
                    and_(
                        TeacherDashboardLayout.teacher_id == teacher_id,
                        TeacherDashboardLayout.is_default == True
                    )
                ).update({"is_default": False})
            
            layout = TeacherDashboardLayout(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                layout_name=layout_data.layout_name,
                layout_description=layout_data.layout_description,
                is_default=layout_data.is_default
            )
            
            self.db.add(layout)
            self.db.flush()  # Get the ID
            
            # Add widget instances if provided
            if layout_data.widget_instances:
                for widget_instance_data in layout_data.widget_instances:
                    widget_instance = DashboardWidgetInstance(
                        id=str(uuid.uuid4()),
                        layout_id=layout.id,
                        widget_id=widget_instance_data.widget_id,
                        position_x=widget_instance_data.position_x,
                        position_y=widget_instance_data.position_y,
                        width=widget_instance_data.width,
                        height=widget_instance_data.height,
                        widget_config=widget_instance_data.widget_config
                    )
                    self.db.add(widget_instance)
            
            self.db.commit()
            
            return self._layout_to_response(layout)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create dashboard layout: {str(e)}")

    def get_teacher_dashboard_layouts(
        self, 
        teacher_id: str, 
        include_inactive: bool = False
    ) -> List[TeacherDashboardLayoutResponse]:
        """Get all dashboard layouts for a teacher"""
        query = self.db.query(TeacherDashboardLayout).filter(
            TeacherDashboardLayout.teacher_id == teacher_id
        )
        
        if not include_inactive:
            query = query.filter(TeacherDashboardLayout.is_active == True)
        
        layouts = query.order_by(desc(TeacherDashboardLayout.is_default), asc(TeacherDashboardLayout.layout_name)).all()
        
        return [self._layout_to_response(layout) for layout in layouts]

    def get_default_dashboard_layout(
        self, 
        teacher_id: str
    ) -> Optional[TeacherDashboardLayoutResponse]:
        """Get the default dashboard layout for a teacher"""
        layout = self.db.query(TeacherDashboardLayout).filter(
            and_(
                TeacherDashboardLayout.teacher_id == teacher_id,
                TeacherDashboardLayout.is_default == True,
                TeacherDashboardLayout.is_active == True
            )
        ).first()
        
        if not layout:
            # Create default layout if none exists
            layout = self._create_default_layout(teacher_id)
        
        return self._layout_to_response(layout) if layout else None

    def update_dashboard_layout(
        self, 
        layout_id: str, 
        teacher_id: str, 
        update_data: TeacherDashboardLayoutUpdate
    ) -> Optional[TeacherDashboardLayoutResponse]:
        """Update a dashboard layout"""
        layout = self.db.query(TeacherDashboardLayout).filter(
            and_(
                TeacherDashboardLayout.id == layout_id,
                TeacherDashboardLayout.teacher_id == teacher_id
            )
        ).first()
        
        if not layout:
            return None
        
        # If setting as default, unset other defaults
        if update_data.is_default:
            self.db.query(TeacherDashboardLayout).filter(
                and_(
                    TeacherDashboardLayout.teacher_id == teacher_id,
                    TeacherDashboardLayout.id != layout_id,
                    TeacherDashboardLayout.is_default == True
                )
            ).update({"is_default": False})
        
        # Update layout fields
        for field, value in update_data.dict(exclude_unset=True).items():
            if field != "widget_instances":
                setattr(layout, field, value)
        
        # Update widget instances if provided
        if update_data.widget_instances is not None:
            # Delete existing widget instances
            self.db.query(DashboardWidgetInstance).filter(
                DashboardWidgetInstance.layout_id == layout_id
            ).delete()
            
            # Add new widget instances
            for widget_instance_data in update_data.widget_instances:
                widget_instance = DashboardWidgetInstance(
                    id=str(uuid.uuid4()),
                    layout_id=layout.id,
                    widget_id=widget_instance_data.widget_id,
                    position_x=widget_instance_data.position_x,
                    position_y=widget_instance_data.position_y,
                    width=widget_instance_data.width,
                    height=widget_instance_data.height,
                    widget_config=widget_instance_data.widget_config
                )
                self.db.add(widget_instance)
        
        layout.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._layout_to_response(layout)

    def delete_dashboard_layout(self, layout_id: str, teacher_id: str) -> bool:
        """Delete a dashboard layout"""
        layout = self.db.query(TeacherDashboardLayout).filter(
            and_(
                TeacherDashboardLayout.id == layout_id,
                TeacherDashboardLayout.teacher_id == teacher_id
            )
        ).first()
        
        if not layout:
            return False
        
        # Don't allow deletion of default layout
        if layout.is_default:
            return False
        
        self.db.delete(layout)
        self.db.commit()
        
        return True

    # ==================== WIDGET MANAGEMENT ====================
    
    def get_available_widgets(self) -> List[BetaDashboardWidgetResponse]:
        """Get all available dashboard widgets"""
        widgets = self.db.query(BetaDashboardWidget).filter(
            BetaDashboardWidget.is_active == True
        ).order_by(asc(BetaDashboardWidget.created_at)).all()
        
        return [self._widget_to_response(widget) for widget in widgets]

    def add_widget_to_layout(
        self, 
        layout_id: str, 
        teacher_id: str, 
        widget_instance_data: BetaDashboardWidgetInstanceCreate
    ) -> Optional[BetaDashboardWidgetInstanceResponse]:
        """Add a widget to a dashboard layout"""
        # Verify layout ownership
        layout = self.db.query(TeacherDashboardLayout).filter(
            and_(
                TeacherDashboardLayout.id == layout_id,
                TeacherDashboardLayout.teacher_id == teacher_id
            )
        ).first()
        
        if not layout:
            return None
        
        widget_instance = DashboardWidgetInstance(
            id=str(uuid.uuid4()),
            layout_id=layout_id,
            widget_id=widget_instance_data.widget_id,
            position_x=widget_instance_data.position_x,
            position_y=widget_instance_data.position_y,
            width=widget_instance_data.width,
            height=widget_instance_data.height,
            widget_config=widget_instance_data.widget_config
        )
        
        self.db.add(widget_instance)
        self.db.commit()
        
        return self._widget_instance_to_response(widget_instance)

    def update_widget_instance(
        self, 
        instance_id: str, 
        teacher_id: str, 
        update_data: BetaDashboardWidgetInstanceUpdate
    ) -> Optional[BetaDashboardWidgetInstanceResponse]:
        """Update a widget instance"""
        widget_instance = self.db.query(DashboardWidgetInstance).join(TeacherDashboardLayout).filter(
            and_(
                DashboardWidgetInstance.id == instance_id,
                TeacherDashboardLayout.teacher_id == teacher_id
            )
        ).first()
        
        if not widget_instance:
            return None
        
        # Update widget instance fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(widget_instance, field, value)
        
        widget_instance.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._widget_instance_to_response(widget_instance)

    def remove_widget_from_layout(
        self, 
        instance_id: str, 
        teacher_id: str
    ) -> bool:
        """Remove a widget from a dashboard layout"""
        widget_instance = self.db.query(DashboardWidgetInstance).join(TeacherDashboardLayout).filter(
            and_(
                DashboardWidgetInstance.id == instance_id,
                TeacherDashboardLayout.teacher_id == teacher_id
            )
        ).first()
        
        if not widget_instance:
            return False
        
        self.db.delete(widget_instance)
        self.db.commit()
        
        return True

    # ==================== ACTIVITY LOGGING ====================
    
    def log_teacher_activity(
        self, 
        teacher_id: str, 
        activity_data: TeacherActivityLogCreate
    ) -> TeacherActivityLogResponse:
        """Log teacher activity"""
        activity_log = TeacherActivityLog(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            activity_type=activity_data.activity_type,
            activity_description=activity_data.activity_description,
            resource_type=activity_data.resource_type,
            resource_id=activity_data.resource_id,
            resource_title=activity_data.resource_title,
            activity_metadata=activity_data.metadata,
            ip_address=activity_data.ip_address,
            user_agent=activity_data.user_agent,
            session_id=activity_data.session_id
        )
        
        self.db.add(activity_log)
        self.db.commit()
        
        # Update achievement progress based on activity
        self._update_achievement_progress(teacher_id, activity_data.activity_type)
        
        return self._activity_log_to_response(activity_log)

    def get_teacher_activity_logs(
        self, 
        teacher_id: str, 
        activity_type: Optional[str] = None,
        days: int = 30,
        limit: int = 100,
        offset: int = 0
    ) -> List[TeacherActivityLogResponse]:
        """Get teacher activity logs"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(TeacherActivityLog).filter(
            and_(
                TeacherActivityLog.teacher_id == teacher_id,
                TeacherActivityLog.created_at >= start_date
            )
        )
        
        if activity_type:
            query = query.filter(TeacherActivityLog.activity_type == activity_type)
        
        logs = query.order_by(desc(TeacherActivityLog.created_at)).offset(offset).limit(limit).all()
        
        return [self._activity_log_to_response(log) for log in logs]

    # ==================== NOTIFICATIONS ====================
    
    def get_teacher_notifications(
        self, 
        teacher_id: str, 
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[TeacherNotificationResponse]:
        """Get teacher notifications"""
        query = self.db.query(TeacherNotification).filter(
            TeacherNotification.teacher_id == teacher_id
        )
        
        if unread_only:
            query = query.filter(TeacherNotification.is_read == False)
        
        # Filter out expired notifications
        query = query.filter(
            or_(
                TeacherNotification.expires_at.is_(None),
                TeacherNotification.expires_at > datetime.utcnow()
            )
        )
        
        notifications = query.order_by(desc(TeacherNotification.is_important), desc(TeacherNotification.created_at)).offset(offset).limit(limit).all()
        
        return [self._notification_to_response(notification) for notification in notifications]

    def mark_notification_as_read(
        self, 
        notification_id: str, 
        teacher_id: str
    ) -> bool:
        """Mark a notification as read"""
        notification = self.db.query(TeacherNotification).filter(
            and_(
                TeacherNotification.id == notification_id,
                TeacherNotification.teacher_id == teacher_id
            )
        ).first()
        
        if not notification:
            return False
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        self.db.commit()
        
        return True

    def mark_all_notifications_as_read(self, teacher_id: str) -> int:
        """Mark all notifications as read for a teacher"""
        result = self.db.query(TeacherNotification).filter(
            and_(
                TeacherNotification.teacher_id == teacher_id,
                TeacherNotification.is_read == False
            )
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        self.db.commit()
        return result

    def create_notification(
        self, 
        teacher_id: str, 
        notification_type: str,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        is_important: bool = False,
        expires_at: Optional[datetime] = None
    ) -> TeacherNotificationResponse:
        """Create a notification for a teacher"""
        notification = TeacherNotification(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            notification_type=notification_type,
            title=title,
            message=message,
            action_url=action_url,
            action_label=action_label,
            is_important=is_important,
            expires_at=expires_at
        )
        
        self.db.add(notification)
        self.db.commit()
        
        return self._notification_to_response(notification)

    # ==================== ACHIEVEMENTS ====================
    
    def get_teacher_achievements(
        self, 
        teacher_id: str, 
        completed_only: bool = False
    ) -> List[TeacherAchievementProgressResponse]:
        """Get teacher achievement progress"""
        query = self.db.query(TeacherAchievementProgress).join(TeacherAchievement).filter(
            TeacherAchievementProgress.teacher_id == teacher_id
        )
        
        if completed_only:
            query = query.filter(TeacherAchievementProgress.is_completed == True)
        
        achievements = query.order_by(desc(TeacherAchievementProgress.completed_at), asc(TeacherAchievement.achievement_name)).all()
        
        return [self._achievement_progress_to_response(achievement) for achievement in achievements]

    def get_available_achievements(self) -> List[TeacherAchievementResponse]:
        """Get all available achievements"""
        achievements = self.db.query(TeacherAchievement).filter(
            TeacherAchievement.is_active == True
        ).order_by(asc(TeacherAchievement.achievement_name)).all()
        
        return [self._achievement_to_response(achievement) for achievement in achievements]

    # ==================== QUICK ACTIONS ====================
    
    def get_teacher_quick_actions(
        self, 
        teacher_id: str
    ) -> List[TeacherQuickActionResponse]:
        """Get teacher's quick actions"""
        actions = self.db.query(TeacherQuickAction).filter(
            and_(
                TeacherQuickAction.teacher_id == teacher_id,
                TeacherQuickAction.is_active == True
            )
        ).order_by(asc(TeacherQuickAction.display_order)).all()
        
        return [self._quick_action_to_response(action) for action in actions]

    def create_quick_action(
        self, 
        teacher_id: str, 
        action_data: TeacherQuickActionCreate
    ) -> TeacherQuickActionResponse:
        """Create a quick action for a teacher"""
        action = TeacherQuickAction(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            action_name=action_data.action_name,
            action_description=action_data.action_description,
            action_type=action_data.action_type,
            action_url=action_data.action_url,
            icon_name=action_data.icon_name,
            color_code=action_data.color_code,
            display_order=action_data.display_order
        )
        
        self.db.add(action)
        self.db.commit()
        
        return self._quick_action_to_response(action)

    def update_quick_action(
        self, 
        action_id: str, 
        teacher_id: str, 
        update_data: TeacherQuickActionUpdate
    ) -> Optional[TeacherQuickActionResponse]:
        """Update a quick action"""
        action = self.db.query(TeacherQuickAction).filter(
            and_(
                TeacherQuickAction.id == action_id,
                TeacherQuickAction.teacher_id == teacher_id
            )
        ).first()
        
        if not action:
            return None
        
        # Update action fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(action, field, value)
        
        action.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._quick_action_to_response(action)

    def delete_quick_action(self, action_id: str, teacher_id: str) -> bool:
        """Delete a quick action"""
        action = self.db.query(TeacherQuickAction).filter(
            and_(
                TeacherQuickAction.id == action_id,
                TeacherQuickAction.teacher_id == teacher_id
            )
        ).first()
        
        if not action:
            return False
        
        self.db.delete(action)
        self.db.commit()
        
        return True

    # ==================== PREFERENCES ====================
    
    def get_teacher_preferences(
        self, 
        teacher_id: str
    ) -> List[BetaTeacherPreferenceResponse]:
        """Get teacher preferences"""
        preferences = self.db.query(BetaTeacherPreference).filter(
            BetaTeacherPreference.teacher_id == teacher_id
        ).order_by(asc(BetaTeacherPreference.preference_key)).all()
        
        return [self._preference_to_response(preference) for preference in preferences]

    def set_teacher_preference(
        self, 
        teacher_id: str, 
        preference_data: BetaTeacherPreferenceCreate
    ) -> BetaTeacherPreferenceResponse:
        """Set a teacher preference"""
        # Check if preference already exists
        existing = self.db.query(BetaTeacherPreference).filter(
            and_(
                BetaTeacherPreference.teacher_id == teacher_id,
                BetaTeacherPreference.preference_key == preference_data.preference_key
            )
        ).first()
        
        if existing:
            # Update existing preference
            existing.preference_value = preference_data.preference_value
            existing.preference_type = preference_data.preference_type
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            return self._preference_to_response(existing)
        
        # Create new preference
        preference = BetaTeacherPreference(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            preference_key=preference_data.preference_key,
            preference_value=preference_data.preference_value,
            preference_type=preference_data.preference_type
        )
        
        self.db.add(preference)
        self.db.commit()
        
        return self._preference_to_response(preference)

    # ==================== STATISTICS ====================
    
    def get_teacher_statistics(
        self, 
        teacher_id: str, 
        stat_type: str = "daily",
        days: int = 30
    ) -> List[TeacherStatisticsResponse]:
        """Get teacher statistics"""
        start_date = date.today() - timedelta(days=days)
        
        stats = self.db.query(TeacherStatistics).filter(
            and_(
                TeacherStatistics.teacher_id == teacher_id,
                TeacherStatistics.stat_type == stat_type,
                TeacherStatistics.stat_date >= start_date
            )
        ).order_by(desc(TeacherStatistics.stat_date)).all()
        
        return [self._statistics_to_response(stat) for stat in stats]

    def update_teacher_statistics(
        self, 
        teacher_id: str, 
        stat_date: date,
        stat_type: str,
        **kwargs
    ) -> TeacherStatisticsResponse:
        """Update teacher statistics"""
        # Check if statistics already exist for this date
        existing = self.db.query(TeacherStatistics).filter(
            and_(
                TeacherStatistics.teacher_id == teacher_id,
                TeacherStatistics.stat_date == stat_date,
                TeacherStatistics.stat_type == stat_type
            )
        ).first()
        
        if existing:
            # Update existing statistics
            for key, value in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            self.db.commit()
            return self._statistics_to_response(existing)
        
        # Create new statistics
        stats = TeacherStatistics(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            stat_date=stat_date,
            stat_type=stat_type,
            **kwargs
        )
        
        self.db.add(stats)
        self.db.commit()
        
        return self._statistics_to_response(stats)

    # ==================== GOALS ====================
    
    def get_teacher_goals(
        self, 
        teacher_id: str, 
        active_only: bool = True
    ) -> List[TeacherGoalResponse]:
        """Get teacher goals"""
        query = self.db.query(TeacherGoal).filter(
            TeacherGoal.teacher_id == teacher_id
        )
        
        if active_only:
            query = query.filter(TeacherGoal.is_active == True)
        
        goals = query.order_by(desc(TeacherGoal.priority_level), asc(TeacherGoal.target_date)).all()
        
        return [self._goal_to_response(goal) for goal in goals]

    def create_goal(
        self, 
        teacher_id: str, 
        goal_data: TeacherGoalCreate
    ) -> TeacherGoalResponse:
        """Create a teacher goal"""
        goal = TeacherGoal(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            goal_title=goal_data.goal_title,
            goal_description=goal_data.goal_description,
            goal_type=goal_data.goal_type,
            goal_category=goal_data.goal_category,
            target_value=goal_data.target_value,
            target_date=goal_data.target_date,
            priority_level=goal_data.priority_level
        )
        
        self.db.add(goal)
        self.db.commit()
        
        return self._goal_to_response(goal)

    def update_goal_progress(
        self, 
        goal_id: str, 
        teacher_id: str, 
        progress_value: int
    ) -> Optional[TeacherGoalResponse]:
        """Update goal progress"""
        goal = self.db.query(TeacherGoal).filter(
            and_(
                TeacherGoal.id == goal_id,
                TeacherGoal.teacher_id == teacher_id
            )
        ).first()
        
        if not goal:
            return None
        
        goal.current_value = progress_value
        
        # Check if goal is completed
        if progress_value >= goal.target_value and not goal.is_completed:
            goal.is_completed = True
            goal.completed_at = datetime.utcnow()
        
        goal.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._goal_to_response(goal)

    # ==================== LEARNING PATHS ====================
    
    def get_teacher_learning_paths(
        self, 
        teacher_id: str, 
        active_only: bool = True
    ) -> List[TeacherLearningPathResponse]:
        """Get teacher learning paths"""
        query = self.db.query(TeacherLearningPath).filter(
            TeacherLearningPath.teacher_id == teacher_id
        )
        
        if active_only:
            query = query.filter(TeacherLearningPath.is_active == True)
        
        paths = query.order_by(desc(TeacherLearningPath.is_completed), asc(TeacherLearningPath.path_name)).all()
        
        return [self._learning_path_to_response(path) for path in paths]

    def create_learning_path(
        self, 
        teacher_id: str, 
        path_data: TeacherLearningPathCreate
    ) -> TeacherLearningPathResponse:
        """Create a learning path for a teacher"""
        path = TeacherLearningPath(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            path_name=path_data.path_name,
            path_description=path_data.path_description,
            path_category=path_data.path_category,
            difficulty_level=path_data.difficulty_level,
            estimated_hours=path_data.estimated_hours
        )
        
        self.db.add(path)
        self.db.flush()  # Get the ID
        
        # Add learning path steps if provided
        if path_data.steps:
            for i, step_data in enumerate(path_data.steps):
                step = LearningPathStep(
                    id=str(uuid.uuid4()),
                    learning_path_id=path.id,
                    step_title=step_data.step_title,
                    step_description=step_data.step_description,
                    step_type=step_data.step_type,
                    step_url=step_data.step_url,
                    step_content=step_data.step_content,
                    estimated_minutes=step_data.estimated_minutes,
                    step_order=i + 1
                )
                self.db.add(step)
        
        self.db.commit()
        
        return self._learning_path_to_response(path)

    # ==================== DASHBOARD ANALYTICS ====================
    
    def get_dashboard_analytics(
        self, 
        teacher_id: str, 
        days: int = 30
    ) -> DashboardAnalyticsResponse:
        """Get comprehensive dashboard analytics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Activity summary
        activity_summary = self.db.query(
            TeacherActivityLog.activity_type,
            func.count(TeacherActivityLog.id).label('count')
        ).filter(
            and_(
                TeacherActivityLog.teacher_id == teacher_id,
                TeacherActivityLog.created_at >= start_date
            )
        ).group_by(TeacherActivityLog.activity_type).all()
        
        # Recent achievements
        recent_achievements = self.db.query(TeacherAchievementProgress).filter(
            and_(
                TeacherAchievementProgress.teacher_id == teacher_id,
                TeacherAchievementProgress.is_completed == True,
                TeacherAchievementProgress.completed_at >= start_date
            )
        ).order_by(desc(TeacherAchievementProgress.completed_at)).limit(5).all()
        
        # Goal progress
        active_goals = self.db.query(TeacherGoal).filter(
            and_(
                TeacherGoal.teacher_id == teacher_id,
                TeacherGoal.is_active == True,
                TeacherGoal.is_completed == False
            )
        ).all()
        
        # Notification count
        unread_notifications = self.db.query(func.count(TeacherNotification.id)).filter(
            and_(
                TeacherNotification.teacher_id == teacher_id,
                TeacherNotification.is_read == False
            )
        ).scalar()
        
        return DashboardAnalyticsResponse(
            total_widgets=self.db.query(func.count(BetaDashboardWidget.id)).scalar() or 0,
            active_widgets=self.db.query(func.count(BetaDashboardWidget.id)).filter(BetaDashboardWidget.is_active == True).scalar() or 0,
            widget_usage_stats={item.activity_type: item.count for item in activity_summary},
            recent_activity=[achievement.__dict__ for achievement in recent_achievements[:5]] if recent_achievements else [],
            performance_metrics={
                "completion_rate": self._calculate_completion_rate(teacher_id),
                "unread_notifications": unread_notifications,
                "total_achievements": self.db.query(func.count(TeacherAchievementProgress.id)).filter(
                    and_(
                        TeacherAchievementProgress.teacher_id == teacher_id,
                        TeacherAchievementProgress.is_completed == True
                    )
                ).scalar() or 0
            },
            last_updated=datetime.utcnow()
        )

    def get_dashboard_summary(
        self, 
        teacher_id: str
    ) -> TeacherDashboardSummaryResponse:
        """Get dashboard summary for quick overview"""
        # Get recent activity count
        recent_activity_count = self.db.query(func.count(TeacherActivityLog.id)).filter(
            and_(
                TeacherActivityLog.teacher_id == teacher_id,
                TeacherActivityLog.created_at >= datetime.utcnow() - timedelta(days=7)
            )
        ).scalar()
        
        # Get unread notifications count
        unread_notifications = self.db.query(func.count(TeacherNotification.id)).filter(
            and_(
                TeacherNotification.teacher_id == teacher_id,
                TeacherNotification.is_read == False
            )
        ).scalar()
        
        # Get active goals count
        active_goals = self.db.query(func.count(TeacherGoal.id)).filter(
            and_(
                TeacherGoal.teacher_id == teacher_id,
                TeacherGoal.is_active == True,
                TeacherGoal.is_completed == False
            )
        ).scalar()
        
        # Get learning paths in progress
        learning_paths_in_progress = self.db.query(func.count(TeacherLearningPath.id)).filter(
            and_(
                TeacherLearningPath.teacher_id == teacher_id,
                TeacherLearningPath.is_active == True,
                TeacherLearningPath.is_completed == False
            )
        ).scalar()
        
        return TeacherDashboardSummaryResponse(
            teacher_id=teacher_id,
            total_widgets=self.db.query(func.count(BetaDashboardWidget.id)).scalar() or 0,
            active_widgets=self.db.query(func.count(BetaDashboardWidget.id)).filter(BetaDashboardWidget.is_active == True).scalar() or 0,
            total_achievements=self.db.query(func.count(TeacherAchievementProgress.id)).filter(TeacherAchievementProgress.teacher_id == teacher_id).scalar() or 0,
            total_goals=self.db.query(func.count(TeacherGoal.id)).filter(TeacherGoal.teacher_id == teacher_id).scalar() or 0,
            active_goals=active_goals
        )

    # ==================== HELPER METHODS ====================
    
    def _create_default_layout(self, teacher_id: str) -> Optional[TeacherDashboardLayout]:
        """Create default dashboard layout for a teacher"""
        try:
            # Get default widgets
            default_widgets = self.db.query(BetaDashboardWidget).filter(
                BetaDashboardWidget.is_system_widget == True
            ).order_by(asc(BetaDashboardWidget.created_at)).all()
            
            # Create default layout
            layout = TeacherDashboardLayout(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                layout_name="Default Layout",
                layout_description="Default dashboard layout",
                is_default=True
            )
            
            self.db.add(layout)
            self.db.flush()
            
            # Add default widgets
            for i, widget in enumerate(default_widgets):
                widget_instance = DashboardWidgetInstance(
                    id=str(uuid.uuid4()),
                    layout_id=layout.id,
                    widget_id=widget.id,
                    position_x=(i % 3) * 4,
                    position_y=(i // 3) * 3,
                    width=4,
                    height=3,
                    widget_config=widget.widget_config
                )
                self.db.add(widget_instance)
            
            self.db.commit()
            return layout
            
        except Exception as e:
            self.db.rollback()
            return None

    def _update_achievement_progress(self, teacher_id: str, activity_type: str) -> None:
        """Update achievement progress based on activity"""
        # This would contain logic to update specific achievements
        # based on the activity type (e.g., lessons created, resources uploaded)
        pass

    def _calculate_completion_rate(self, teacher_id: str) -> float:
        """Calculate overall completion rate for teacher goals and learning paths"""
        total_items = self.db.query(func.count(TeacherGoal.id)).filter(
            TeacherGoal.teacher_id == teacher_id
        ).scalar() + self.db.query(func.count(TeacherLearningPath.id)).filter(
            TeacherLearningPath.teacher_id == teacher_id
        ).scalar()
        
        if total_items == 0:
            return 0.0
        
        completed_items = self.db.query(func.count(TeacherGoal.id)).filter(
            and_(
                TeacherGoal.teacher_id == teacher_id,
                TeacherGoal.is_completed == True
            )
        ).scalar() + self.db.query(func.count(TeacherLearningPath.id)).filter(
            and_(
                TeacherLearningPath.teacher_id == teacher_id,
                TeacherLearningPath.is_completed == True
            )
        ).scalar()
        
        return (completed_items / total_items) * 100.0

    def _get_last_login(self, teacher_id: str) -> Optional[datetime]:
        """Get teacher's last login time"""
        last_login = self.db.query(TeacherActivityLog.created_at).filter(
            and_(
                TeacherActivityLog.teacher_id == teacher_id,
                TeacherActivityLog.activity_type == "login"
            )
        ).order_by(desc(TeacherActivityLog.created_at)).first()
        
        return last_login[0] if last_login else None

    # ==================== RESPONSE CONVERTERS ====================
    
    def _layout_to_response(self, layout: TeacherDashboardLayout) -> TeacherDashboardLayoutResponse:
        """Convert layout model to response"""
        # Get widget instances
        widget_instances = self.db.query(DashboardWidgetInstance).filter(
            DashboardWidgetInstance.layout_id == layout.id
        ).order_by(asc(DashboardWidgetInstance.position_y), asc(DashboardWidgetInstance.position_x)).all()
        
        return TeacherDashboardLayoutResponse(
            id=layout.id,
            teacher_id=layout.teacher_id,
            layout_name=layout.layout_name,
            layout_description=layout.layout_description,
            is_default=layout.is_default,
            is_active=layout.is_active,
            created_at=layout.created_at,
            updated_at=layout.updated_at,
            widget_instances=[self._widget_instance_to_response(instance) for instance in widget_instances]
        )

    def _widget_to_response(self, widget: BetaDashboardWidget) -> BetaDashboardWidgetResponse:
        """Convert widget model to response"""
        # Map existing columns to response
        widget_name = getattr(widget, 'widget_name', None) or getattr(widget, 'name', 'Unknown Widget')
        widget_description = getattr(widget, 'widget_description', None) or getattr(widget, 'description', '')
        widget_config = getattr(widget, 'widget_config', None) or getattr(widget, 'configuration', {})
        is_system_widget = getattr(widget, 'is_system_widget', False)
        display_order = getattr(widget, 'display_order', 0)
        
        return BetaDashboardWidgetResponse(
            id=str(widget.id) if widget.id else '',
            name=widget_name,
            widget_type=getattr(widget, 'widget_type', ''),
            configuration=widget_config,
            is_active=getattr(widget, 'is_active', True),
            created_at=getattr(widget, 'created_at', datetime.utcnow()),
            updated_at=getattr(widget, 'updated_at', None) or datetime.utcnow()
        )

    def _widget_instance_to_response(self, instance: DashboardWidgetInstance) -> BetaDashboardWidgetInstanceResponse:
        """Convert widget instance model to response"""
        return BetaDashboardWidgetInstanceResponse(
            id=instance.id,
            layout_id=instance.layout_id,
            widget_id=instance.widget_id,
            position_x=instance.position_x,
            position_y=instance.position_y,
            width=instance.width,
            height=instance.height,
            widget_config=instance.widget_config,
            is_visible=instance.is_visible,
            created_at=instance.created_at,
            updated_at=instance.updated_at
        )

    def _activity_log_to_response(self, log: TeacherActivityLog) -> TeacherActivityLogResponse:
        """Convert activity log model to response"""
        return TeacherActivityLogResponse(
            id=log.id,
            teacher_id=log.teacher_id,
            activity_type=log.activity_type,
            activity_description=log.activity_description,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            resource_title=log.resource_title,
            metadata=log.activity_metadata,
            ip_address=str(log.ip_address) if log.ip_address else None,
            user_agent=log.user_agent,
            session_id=log.session_id,
            created_at=log.created_at
        )

    def _notification_to_response(self, notification: TeacherNotification) -> TeacherNotificationResponse:
        """Convert notification model to response"""
        return TeacherNotificationResponse(
            id=notification.id,
            teacher_id=notification.teacher_id,
            notification_type=notification.notification_type,
            title=notification.title,
            message=notification.message,
            action_url=notification.action_url,
            action_label=notification.action_label,
            is_read=notification.is_read,
            is_important=notification.is_important,
            expires_at=notification.expires_at,
            created_at=notification.created_at,
            read_at=notification.read_at
        )

    def _achievement_to_response(self, achievement: TeacherAchievement) -> TeacherAchievementResponse:
        """Convert achievement model to response"""
        return TeacherAchievementResponse(
            id=achievement.id,
            achievement_code=achievement.achievement_code,
            achievement_name=achievement.achievement_name,
            achievement_description=achievement.achievement_description,
            achievement_category=achievement.achievement_category,
            icon_name=achievement.icon_name,
            color_code=achievement.color_code,
            points=achievement.points,
            is_active=achievement.is_active,
            created_at=achievement.created_at
        )

    def _achievement_progress_to_response(self, progress: TeacherAchievementProgress) -> TeacherAchievementProgressResponse:
        """Convert achievement progress model to response"""
        achievement = self.db.query(TeacherAchievement).filter(
            TeacherAchievement.id == progress.achievement_id
        ).first()
        
        return TeacherAchievementProgressResponse(
            id=progress.id,
            teacher_id=progress.teacher_id,
            achievement_id=progress.achievement_id,
            achievement=self._achievement_to_response(achievement) if achievement else None,
            progress_value=progress.progress_value,
            target_value=progress.target_value,
            is_completed=progress.is_completed,
            completed_at=progress.completed_at,
            created_at=progress.created_at,
            updated_at=progress.updated_at
        )

    def _quick_action_to_response(self, action: TeacherQuickAction) -> TeacherQuickActionResponse:
        """Convert quick action model to response"""
        return TeacherQuickActionResponse(
            id=action.id,
            teacher_id=action.teacher_id,
            action_name=action.action_name,
            action_description=action.action_description,
            action_type=action.action_type,
            action_url=action.action_url,
            icon_name=action.icon_name,
            color_code=action.color_code,
            display_order=action.display_order,
            is_active=action.is_active,
            created_at=action.created_at,
            updated_at=action.updated_at
        )

    def _preference_to_response(self, preference: BetaTeacherPreference) -> BetaTeacherPreferenceResponse:
        """Convert preference model to response"""
        return BetaTeacherPreferenceResponse(
            id=preference.id,
            teacher_id=preference.teacher_id,
            preference_key=preference.preference_key,
            preference_value=preference.preference_value,
            preference_type=preference.preference_type,
            created_at=preference.created_at,
            updated_at=preference.updated_at
        )

    def _statistics_to_response(self, stats: TeacherStatistics) -> TeacherStatisticsResponse:
        """Convert statistics model to response"""
        return TeacherStatisticsResponse(
            id=stats.id,
            teacher_id=stats.teacher_id,
            stat_date=stats.stat_date,
            stat_type=stats.stat_type,
            lessons_created=stats.lessons_created,
            assessments_created=stats.assessments_created,
            resources_uploaded=stats.resources_uploaded,
            resources_downloaded=stats.resources_downloaded,
            resources_shared=stats.resources_shared,
            resources_received=stats.resources_received,
            collections_created=stats.collections_created,
            reviews_written=stats.reviews_written,
            time_spent_minutes=stats.time_spent_minutes,
            login_count=stats.login_count,
            created_at=stats.created_at
        )

    def _goal_to_response(self, goal: TeacherGoal) -> TeacherGoalResponse:
        """Convert goal model to response"""
        return TeacherGoalResponse(
            id=goal.id,
            teacher_id=goal.teacher_id,
            goal_title=goal.goal_title,
            goal_description=goal.goal_description,
            goal_type=goal.goal_type,
            goal_category=goal.goal_category,
            target_value=goal.target_value,
            current_value=goal.current_value,
            target_date=goal.target_date,
            is_completed=goal.is_completed,
            completed_at=goal.completed_at,
            priority_level=goal.priority_level,
            is_active=goal.is_active,
            created_at=goal.created_at,
            updated_at=goal.updated_at
        )

    def _learning_path_to_response(self, path: TeacherLearningPath) -> TeacherLearningPathResponse:
        """Convert learning path model to response"""
        # Get learning path steps
        steps = self.db.query(LearningPathStep).filter(
            LearningPathStep.learning_path_id == path.id
        ).order_by(asc(LearningPathStep.step_order)).all()
        
        return TeacherLearningPathResponse(
            id=path.id,
            teacher_id=path.teacher_id,
            path_name=path.path_name,
            path_description=path.path_description,
            path_category=path.path_category,
            difficulty_level=path.difficulty_level,
            estimated_hours=path.estimated_hours,
            is_completed=path.is_completed,
            completion_percentage=path.completion_percentage,
            started_at=path.started_at,
            completed_at=path.completed_at,
            is_active=path.is_active,
            created_at=path.created_at,
            updated_at=path.updated_at,
            steps=[self._learning_path_step_to_response(step) for step in steps]
        )

    def _learning_path_step_to_response(self, step: LearningPathStep) -> LearningPathStepResponse:
        """Convert learning path step model to response"""
        return LearningPathStepResponse(
            id=step.id,
            learning_path_id=step.learning_path_id,
            step_title=step.step_title,
            step_description=step.step_description,
            step_type=step.step_type,
            step_url=step.step_url,
            step_content=step.step_content,
            estimated_minutes=step.estimated_minutes,
            is_completed=step.is_completed,
            completed_at=step.completed_at,
            step_order=step.step_order,
            created_at=step.created_at
        )
