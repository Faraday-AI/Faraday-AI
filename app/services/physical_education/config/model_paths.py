import os
import logging
from pathlib import Path
from typing import Dict, Literal, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

# Base model directory - using project-relative path
BASE_MODEL_DIR = Path(__file__).parent.parent.parent.parent / 'models'

# Model paths
ACTIVITY_ADAPTATION_MODEL = BASE_MODEL_DIR / "activity_adaptation/metadata.json"
ACTIVITY_ASSESSMENT_MODEL = BASE_MODEL_DIR / "skill_assessment/metadata.json"
MOVEMENT_ANALYSIS_MODEL = BASE_MODEL_DIR / "movement_analysis/metadata.json"

# Ensure all model directories exist
for path in [ACTIVITY_ADAPTATION_MODEL, ACTIVITY_ASSESSMENT_MODEL, MOVEMENT_ANALYSIS_MODEL]:
    path.parent.mkdir(parents=True, exist_ok=True)

# Model paths configuration
MODEL_PATHS = {
    'activity_adaptation': {
        'model_file': str(BASE_MODEL_DIR / 'activity_adaptation/model.joblib'),
        'metadata_file': str(BASE_MODEL_DIR / 'activity_adaptation/metadata.json')
    },
    'skill_assessment': {
        'model_file': str(BASE_MODEL_DIR / 'skill_assessment/model.joblib'),
        'metadata_file': str(BASE_MODEL_DIR / 'skill_assessment/metadata.json')
    },
    'movement_analysis': {
        'model_file': str(BASE_MODEL_DIR / 'movement_analysis/model.h5'),
        'metadata_file': str(BASE_MODEL_DIR / 'movement_analysis/metadata.json')
    }
}

def get_model_path(model_type: str, file_type: str = 'model_file') -> str:
    """Get the path for a specific model file."""
    return MODEL_PATHS.get(model_type, {}).get(file_type, '')

def ensure_model_directories():
    """Ensure all model directories exist."""
    for model_type in ['activity_adaptation', 'skill_assessment', 'movement_analysis']:
        model_dir = BASE_MODEL_DIR / model_type
        model_dir.mkdir(parents=True, exist_ok=True)

def verify_model_paths() -> Dict[str, Dict[str, Dict[str, bool]]]:
    """Verify that all model paths exist and are accessible."""
    results = {}
    for model_type, paths in MODEL_PATHS.items():
        results[model_type] = {}
        for file_type, path in paths.items():
            file_path = Path(path)
            results[model_type][file_type] = {
                'exists': file_path.exists(),
                'is_file': file_path.is_file() if file_path.exists() else False,
                'is_readable': os.access(path, os.R_OK) if file_path.exists() else False
            }
    return results 