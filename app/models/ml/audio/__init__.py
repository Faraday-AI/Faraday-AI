"""
Audio Analysis Models

This module exports the audio analysis model.
"""

import os
from pathlib import Path

# Get the directory containing this file
MODEL_DIR = Path(__file__).parent

# Define the model path
AUDIO_ANALYSIS_MODEL = MODEL_DIR / "audio_analysis.keras"

__all__ = [
    'AUDIO_ANALYSIS_MODEL'
] 