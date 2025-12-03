from .activity import router as activity_router
from .management.ai_analysis import router as ai_analysis_router
from .core.lesson_plans import router as lesson_plans_router
from .physical_education.physical_education import router as pe_router
from .user_profile import router as user_profile_router
from .user_preferences import router as user_preferences_router
from .role_management import router as role_management_router
from .permission_management import router as permission_management_router
from .organization_management import router as organization_management_router
from .team_management import router as team_management_router
from .user_analytics import router as user_analytics_router
from .beta_testing import router as beta_testing_router
from . import resource_management, beta_teacher_dashboard, beta_safety, beta_assessment, beta_security, beta_resource_management, dashboard_resource_management, dashboard_context_analytics, beta_context_analytics, dashboard_preferences, beta_dashboard_preferences, beta_avatars_voices
from . import microsoft_auth, beta_microsoft_auth, microsoft_calendar, beta_microsoft_calendar, microsoft_health, speech_to_text, text_to_speech, guest_chat, ai_assistant, sms_subscription

__all__ = [
    'activity_router',
    'ai_analysis_router',
    'lesson_plans_router',
    'pe_router',
    'user_profile_router',
    'user_preferences_router',
    'role_management_router',
    'permission_management_router',
    'organization_management_router',
    'team_management_router',
    'user_analytics_router',
    'beta_testing_router',
    'resource_management',
    'beta_teacher_dashboard',
    'beta_safety',
    'beta_assessment',
    'beta_security',
    'beta_resource_management',
    'dashboard_resource_management',
    'dashboard_context_analytics',
    'beta_context_analytics',
    'dashboard_preferences',
    'beta_dashboard_preferences',
    'beta_avatars_voices',
    'microsoft_auth',
    'beta_microsoft_auth',
    'microsoft_calendar',
    'beta_microsoft_calendar',
    'microsoft_health',
    'speech_to_text',
    'text_to_speech',
    'guest_chat',
    'ai_assistant',
    'sms_subscription'
] 