import os
import logging
from pathlib import Path
from typing import Dict, Literal, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

# Base model directory
BASE_MODEL_DIR = Path('/app/services/physical_education/models')

# Ensure the directory exists
BASE_MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Model paths
ACTIVITY_ADAPTATION_MODEL = BASE_MODEL_DIR / "activity_adaptation_metadata.json"
ACTIVITY_ASSESSMENT_MODEL = BASE_MODEL_DIR / "activity_assessment_metadata.json"
MOVEMENT_ANALYSIS_MODEL = BASE_MODEL_DIR / "movement_analysis_metadata.json"

# Ensure all model directories exist
for path in [ACTIVITY_ADAPTATION_MODEL, ACTIVITY_ASSESSMENT_MODEL, MOVEMENT_ANALYSIS_MODEL]:
    path.parent.mkdir(parents=True, exist_ok=True)

# Model paths configuration
MODEL_PATHS = {
    'activity_adaptation': {
        'model_file': str(BASE_MODEL_DIR / 'activity_adaptation/activity_adaptation.joblib'),
        'metadata_file': str(BASE_MODEL_DIR / 'activity_adaptation/activity_adaptation_metadata.json')
    },
    'skill_assessment': {
        'model_file': str(BASE_MODEL_DIR / 'skill_assessment/skill_assessment.joblib'),
        'metadata_file': str(BASE_MODEL_DIR / 'skill_assessment/skill_assessment_metadata.json')
    },
    'movement_analysis': {
        'model_file': str(BASE_MODEL_DIR / 'movement_analysis/movement_analysis.h5'),
        'metadata_file': str(BASE_MODEL_DIR / 'movement_analysis/movement_analysis_metadata.json')
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
    """
    Verify that all model paths exist and are accessible.
    
    Returns:
        Dictionary containing verification results for each model type
    """
    results = {}
    try:
        for model_type in MODEL_PATHS.keys():
            model_dir = BASE_MODEL_DIR / model_type
            model_file = Path(MODEL_PATHS[model_type]['model_file'])
            metadata_file = Path(MODEL_PATHS[model_type]['metadata_file'])
            
            results[model_type] = {
                'directory': {
                    'exists': model_dir.exists(),
                    'is_dir': model_dir.is_dir()
                },
                'model_file': {
                    'exists': model_file.exists(),
                    'is_file': model_file.is_file()
                },
                'metadata_file': {
                    'exists': metadata_file.exists(),
                    'is_file': metadata_file.is_file()
                }
            }
            
            logger.info(f"Verified paths for {model_type}: {results[model_type]}")
            
        return results
        
    except Exception as e:
        logger.error(f"Error verifying model paths: {str(e)}")
        raise 