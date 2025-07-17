"""
Movement Models

This module exports the movement analysis models and configurations.
"""

import os
from pathlib import Path

# Get the directory containing this file
MODEL_DIR = Path(__file__).parent

# Define the model paths
MOVEMENT_ANALYSIS_MODEL = MODEL_DIR / "movement_analysis_model.h5"
MOVEMENT_MODELS_CONFIG = MODEL_DIR / "movement_models.json"

# Import the models module
# Removed MovementAnalysis and MovementPattern imports and exports as they are now canonical elsewhere

__all__ = [
    'MOVEMENT_ANALYSIS_MODEL',
    'MOVEMENT_MODELS_CONFIG'
] 