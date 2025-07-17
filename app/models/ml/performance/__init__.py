"""
Performance Prediction Models

This module exports the performance prediction model.
"""

import os
from pathlib import Path

# Get the directory containing this file
MODEL_DIR = Path(__file__).parent

# Define the model path
PERFORMANCE_PREDICTION_MODEL = MODEL_DIR / "performance_prediction.keras"

__all__ = [
    'PERFORMANCE_PREDICTION_MODEL'
] 