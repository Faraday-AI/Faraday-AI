"""
Optimization Configuration for Jasper AI Assistant
Controls which performance optimizations are enabled.
"""

import os
from typing import Optional

class OptimizationConfig:
    """Configuration for performance optimizations."""
    
    # Enable/disable optimizations via environment variables
    ENABLE_STREAMING = os.getenv("JASPER_ENABLE_STREAMING", "false").lower() == "true"
    ENABLE_JSON_SCHEMA = os.getenv("JASPER_ENABLE_JSON_SCHEMA", "false").lower() == "true"
    ENABLE_TWO_MODEL_PIPELINE = os.getenv("JASPER_ENABLE_TWO_MODEL", "false").lower() == "true"
    ENABLE_PARALLELIZATION = os.getenv("JASPER_ENABLE_PARALLEL", "false").lower() == "true"
    
    # Model configuration
    MINI_MODEL = os.getenv("JASPER_MINI_MODEL", "gpt-4o-mini")  # For fast intent classification
    MAIN_MODEL = os.getenv("JASPER_MAIN_MODEL", "gpt-4")  # For main responses
    
    # Caching configuration
    ENABLE_CACHING = os.getenv("JASPER_ENABLE_CACHING", "true").lower() == "true"
    CACHE_TTL_MINUTES = int(os.getenv("JASPER_CACHE_TTL_MINUTES", "5"))
    
    # Prompt optimization
    USE_COMPRESSED_PROMPTS = os.getenv("JASPER_USE_COMPRESSED_PROMPTS", "true").lower() == "true"
    
    @classmethod
    def get_optimization_summary(cls) -> dict:
        """Get summary of enabled optimizations."""
        return {
            "streaming": cls.ENABLE_STREAMING,
            "json_schema": cls.ENABLE_JSON_SCHEMA,
            "two_model_pipeline": cls.ENABLE_TWO_MODEL_PIPELINE,
            "parallelization": cls.ENABLE_PARALLELIZATION,
            "caching": cls.ENABLE_CACHING,
            "compressed_prompts": cls.USE_COMPRESSED_PROMPTS,
            "mini_model": cls.MINI_MODEL,
            "main_model": cls.MAIN_MODEL
        }

