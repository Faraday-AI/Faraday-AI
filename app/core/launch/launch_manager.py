from typing import Dict, List, Set
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class FeatureFlag:
    """Controls feature availability during phased rollout"""
    feature_id: str
    enabled: bool
    phase: int
    dependencies: Set[str]
    requires_parent_consent: bool
    requires_admin_setup: bool

class LaunchManager:
    """
    Manages phased feature rollout and ensures seamless future expansion
    of the Faraday AI platform.
    """
    
    def __init__(self):
        self.active_features: Dict[str, FeatureFlag] = {}
        self.phase_history: List[Dict] = []
        self.current_phase = 1
        
        # Initialize core features
        self._initialize_feature_flags()
    
    def _initialize_feature_flags(self):
        """Set up initial feature flags for all planned features"""
        
        # Phase 1 - Core Platform (Essential Features)
        self._add_feature("core_learning", 1, set(), True, True)
        self._add_feature("device_compatibility", 1, {"core_learning"}, False, True)
        self._add_feature("basic_progress_tracking", 1, {"core_learning"}, True, True)
        self._add_feature("parent_dashboard_basic", 1, {"core_learning"}, True, True)
        self._add_feature("security_basic", 1, set(), False, True)
        self._add_feature("attendance_basic", 1, set(), False, True)
        self._add_feature("hallpass_basic", 1, set(), False, True)
        self._add_feature("admin_dashboard_basic", 1, set(), False, True)
        
        # Phase 2 - Enhanced Learning & Security
        self._add_feature("ai_tutoring", 2, {"core_learning"}, True, True)
        self._add_feature("peer_avatars", 2, {"ai_tutoring"}, True, True)
        self._add_feature("security_advanced", 2, {"security_basic"}, False, True)
        self._add_feature("parent_dashboard_advanced", 2, {"parent_dashboard_basic"}, True, True)
        
        # Phase 3 - Administrative Automation
        self._add_feature("hr_automation", 3, {"admin_dashboard_basic"}, False, True)
        self._add_feature("finance_automation", 3, {"admin_dashboard_basic"}, False, True)
        self._add_feature("district_analytics", 3, {"admin_dashboard_basic"}, False, True)
        
        # Phase 4 - Advanced AI Features
        self._add_feature("career_mobility_ai", 4, {"core_learning", "ai_tutoring"}, True, True)
        self._add_feature("cross_school_ai", 4, {"district_analytics"}, False, True)
        self._add_feature("predictive_analytics", 4, {"district_analytics"}, False, True)
    
    def _add_feature(self, feature_id: str, phase: int, dependencies: Set[str],
                    requires_parent_consent: bool, requires_admin_setup: bool):
        """Add a new feature flag"""
        self.active_features[feature_id] = FeatureFlag(
            feature_id=feature_id,
            enabled=phase == 1,  # Only phase 1 features enabled initially
            phase=phase,
            dependencies=dependencies,
            requires_parent_consent=requires_parent_consent,
            requires_admin_setup=requires_admin_setup
        )
    
    def get_available_features(self, user_type: str, grade_level: int = None) -> Dict[str, bool]:
        """Get available features based on user type and grade level"""
        features = {}
        
        for feature_id, flag in self.active_features.items():
            if not flag.enabled:
                features[feature_id] = False
                continue
                
            # Check dependencies
            if not self._are_dependencies_met(flag.dependencies):
                features[feature_id] = False
                continue
            
            # Apply user type restrictions
            features[feature_id] = self._is_feature_available_for_user(
                feature_id, user_type, grade_level
            )
        
        return features
    
    def _are_dependencies_met(self, dependencies: Set[str]) -> bool:
        """Check if all required dependencies are enabled"""
        return all(
            self.active_features.get(dep, FeatureFlag("", False, 0, set(), False, False)).enabled
            for dep in dependencies
        )
    
    def _is_feature_available_for_user(self, feature_id: str, user_type: str, 
                                     grade_level: int = None) -> bool:
        """Determine if a feature is available for a specific user type"""
        if user_type == "admin":
            return True
            
        if user_type == "parent" and not self.active_features[feature_id].requires_parent_consent:
            return False
            
        if user_type == "student" and grade_level:
            # Apply grade-level restrictions
            if feature_id in ["career_mobility_ai", "peer_avatars"]:
                return grade_level >= 6  # Only for 6th grade and up
                
            if feature_id == "ai_tutoring":
                return True  # Available for all grades with appropriate content
        
        return True
    
    def advance_to_phase(self, new_phase: int) -> Dict:
        """Advance the platform to a new phase, enabling associated features"""
        if new_phase <= self.current_phase:
            return {"error": "Cannot revert to a previous phase"}
            
        phase_features = []
        for feature_id, flag in self.active_features.items():
            if flag.phase == new_phase:
                flag.enabled = True
                phase_features.append(feature_id)
        
        self.current_phase = new_phase
        
        transition = {
            "phase": new_phase,
            "date": datetime.now(),
            "features_enabled": phase_features
        }
        self.phase_history.append(transition)
        
        return transition
    
    def get_implementation_status(self) -> Dict:
        """Get current implementation status and available features"""
        return {
            "current_phase": self.current_phase,
            "total_features": len(self.active_features),
            "enabled_features": sum(1 for f in self.active_features.values() if f.enabled),
            "phase_history": self.phase_history,
            "next_phase_features": [
                f.feature_id for f in self.active_features.values()
                if f.phase == self.current_phase + 1
            ]
        }
    
    def can_enable_feature(self, feature_id: str) -> Dict:
        """Check if a feature can be enabled based on dependencies"""
        if feature_id not in self.active_features:
            return {"can_enable": False, "reason": "Feature not found"}
            
        flag = self.active_features[feature_id]
        
        if flag.enabled:
            return {"can_enable": False, "reason": "Feature already enabled"}
            
        if not self._are_dependencies_met(flag.dependencies):
            return {
                "can_enable": False,
                "reason": "Dependencies not met",
                "missing_dependencies": [
                    dep for dep in flag.dependencies
                    if not self.active_features[dep].enabled
                ]
            }
        
        return {
            "can_enable": True,
            "requires_parent_consent": flag.requires_parent_consent,
            "requires_admin_setup": flag.requires_admin_setup
        } 