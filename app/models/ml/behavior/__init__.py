"""
Behavior Analysis Models

This module exports the behavior analysis model.
"""

import os
from pathlib import Path

# Get the directory containing this file
MODEL_DIR = Path(__file__).parent

# Define the model path
BEHAVIOR_ANALYSIS_MODEL = MODEL_DIR / "behavior_analysis.joblib"

__all__ = [
    'BEHAVIOR_ANALYSIS_MODEL'
] 