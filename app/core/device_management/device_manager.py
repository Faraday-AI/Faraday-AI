from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class DeviceSession:
    """Represents an active device session for a student"""
    device_id: str
    device_type: str  # 'Laptop', 'Mobile', 'Tablet'
    user_id: str
    grade_level: int
    start_time: datetime
    last_active: datetime
    is_school_issued: bool
    preferences: Dict

@dataclass
class LearningProgress:
    """Tracks learning progress that can be continued across devices"""
    user_id: str
    current_assignment_id: Optional[str]
    last_completed_module: str
    progress_data: Dict
    last_device: str
    needs_sync: bool
    offline_data: Dict

class DeviceManager:
    """
    Manages device compatibility and session tracking across laptops, mobile devices,
    and tablets for students of all grade levels.
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, DeviceSession] = {}
        self.learning_progress: Dict[str, LearningProgress] = {}
        self.offline_queue: List[Dict] = []
        
    def register_device(self, user_id: str, device_type: str, grade_level: int, 
                       is_school_issued: bool = False) -> DeviceSession:
        """Register a new device for a student"""
        device_id = f"{user_id}_{device_type}_{datetime.now().timestamp()}"
        
        # Set age-appropriate default preferences based on grade level
        preferences = self._get_default_preferences(grade_level, device_type)
        
        session = DeviceSession(
            device_id=device_id,
            device_type=device_type,
            user_id=user_id,
            grade_level=grade_level,
            start_time=datetime.now(),
            last_active=datetime.now(),
            is_school_issued=is_school_issued,
            preferences=preferences
        )
        
        self.active_sessions[device_id] = session
        return session
    
    def _get_default_preferences(self, grade_level: int, device_type: str) -> Dict:
        """Get default UI and learning preferences based on grade level and device"""
        if grade_level <= 5:  # K-5
            return {
                "ui_theme": "elementary",
                "font_size": "large",
                "use_speech_to_text": True,
                "gamification_enabled": True,
                "simplified_navigation": True,
                "parent_oversight_required": True,
                "device_specific": {
                    "laptop": {
                        "keyboard_shortcuts_enabled": False,
                        "mouse_sensitivity": "low",
                        "offline_mode_enabled": True
                    },
                    "mobile": {
                        "touch_targets": "large",
                        "simplified_gestures": True
                    }
                }
            }
        else:  # 6-12
            return {
                "ui_theme": "secondary",
                "font_size": "medium",
                "use_speech_to_text": False,
                "gamification_enabled": False,
                "simplified_navigation": False,
                "parent_oversight_required": False,
                "device_specific": {
                    "laptop": {
                        "keyboard_shortcuts_enabled": True,
                        "mouse_sensitivity": "medium",
                        "offline_mode_enabled": True
                    },
                    "mobile": {
                        "touch_targets": "medium",
                        "simplified_gestures": False
                    }
                }
            }
    
    def start_learning_session(self, user_id: str, device_id: str) -> Dict:
        """Start or resume a learning session on any device"""
        if device_id not in self.active_sessions:
            raise ValueError("Device not registered")
            
        session = self.active_sessions[device_id]
        progress = self.learning_progress.get(user_id)
        
        if not progress:
            # Initialize new progress tracking
            progress = LearningProgress(
                user_id=user_id,
                current_assignment_id=None,
                last_completed_module="",
                progress_data={},
                last_device=device_id,
                needs_sync=False,
                offline_data={}
            )
            self.learning_progress[user_id] = progress
        
        # Update session activity
        session.last_active = datetime.now()
        
        return {
            "session": session,
            "progress": progress,
            "preferences": session.preferences,
            "can_resume": bool(progress.current_assignment_id)
        }
    
    def sync_offline_progress(self, user_id: str, device_id: str, offline_data: Dict) -> bool:
        """Sync offline progress when device regains internet connection"""
        if user_id not in self.learning_progress:
            return False
            
        progress = self.learning_progress[user_id]
        progress.offline_data.update(offline_data)
        progress.needs_sync = False
        progress.last_device = device_id
        
        # Queue offline data for processing
        self.offline_queue.append({
            "user_id": user_id,
            "device_id": device_id,
            "offline_data": offline_data,
            "timestamp": datetime.now()
        })
        
        return True
    
    def update_learning_progress(self, user_id: str, device_id: str, 
                               progress_update: Dict) -> bool:
        """Update learning progress from any device"""
        if user_id not in self.learning_progress:
            return False
            
        progress = self.learning_progress[user_id]
        progress.progress_data.update(progress_update)
        progress.last_device = device_id
        progress.last_completed_module = progress_update.get(
            "completed_module", 
            progress.last_completed_module
        )
        
        return True
    
    def get_device_optimized_content(self, device_id: str) -> Dict:
        """Get device-optimized content and UI settings"""
        if device_id not in self.active_sessions:
            raise ValueError("Device not registered")
            
        session = self.active_sessions[device_id]
        device_specific = session.preferences["device_specific"]
        
        return {
            "ui_settings": device_specific[session.device_type.lower()],
            "grade_level": session.grade_level,
            "offline_enabled": device_specific[session.device_type.lower()]["offline_mode_enabled"],
            "accessibility": self._get_accessibility_settings(session)
        }
    
    def _get_accessibility_settings(self, session: DeviceSession) -> Dict:
        """Get accessibility settings based on grade level and device type"""
        base_settings = {
            "screen_reader_enabled": False,
            "high_contrast": False,
            "animation_reduced": False
        }
        
        if session.grade_level <= 5:
            base_settings.update({
                "text_to_speech_enabled": True,
                "simplified_interface": True
            })
        
        return base_settings 