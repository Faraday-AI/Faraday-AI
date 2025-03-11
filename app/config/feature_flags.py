from pydantic import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class FeatureFlags(BaseSettings):
    # Beta Phase Features
    ENABLE_CHATGPT: bool = True  # Always enabled in beta
    ENABLE_DEBUG_LOGGING: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Optional Integrations
    ENABLE_TWILIO: bool = os.getenv("ENABLE_TWILIO", "false").lower() == "true"
    ENABLE_GOOGLE_CLOUD: bool = os.getenv("ENABLE_GOOGLE_CLOUD", "false").lower() == "true"
    
    # Microsoft Graph Features
    ENABLE_MS_GRAPH: bool = all([
        os.getenv("MSCLIENTID"),
        os.getenv("MSCLIENTSECRET"),
        os.getenv("MSTENANTID")
    ])
    
    # Feature Specific Settings
    ENABLE_STREAMING_RESPONSE: bool = True
    ENABLE_FILE_UPLOAD: bool = True
    ENABLE_ASYNC_PROCESSING: bool = True
    
    # Beta Testing Features
    ENABLE_BETA_FEATURES: bool = os.getenv("APP_ENVIRONMENT") == "beta"
    ENABLE_FEEDBACK_COLLECTION: bool = True
    ENABLE_USAGE_METRICS: bool = True
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        return getattr(self, f"ENABLE_{feature_name.upper()}", False)
    
    class Config:
        env_file = ".env"

feature_flags = FeatureFlags() 