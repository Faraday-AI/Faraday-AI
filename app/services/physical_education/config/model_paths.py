import os
import logging
from pathlib import Path
from typing import Dict, Literal, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

# Use relative path for models directory
BASE_MODEL_DIR = Path(os.getenv('MODEL_DIR', './models'))

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
        'model_file': 'activity_adaptation.joblib',
        'config_file': 'activity_adaptation_config.json'
    },
    'activity_assessment': {
        'model_file': 'activity_assessment.joblib',
        'config_file': 'activity_assessment_config.json'
    },
    'movement_analysis': {
        'model_file': 'movement_analysis.h5',
        'config_file': 'movement_analysis_config.json'
    }
}

def get_model_path(
    model_type: str,
    file_type: Literal['model_file', 'config_file'] = 'model_file'
) -> Path:
    """
    Get the path to a model or config file.
    
    Args:
        model_type: Type of model (e.g., 'activity_adaptation')
        file_type: Type of file to get ('model_file' or 'config_file')
        
    Returns:
        Path to the requested file
        
    Raises:
        ValueError: If model_type or file_type is invalid
    """
    try:
        if model_type not in MODEL_PATHS:
            raise ValueError(f"Invalid model type: {model_type}")
        if file_type not in ['model_file', 'config_file']:
            raise ValueError(f"Invalid file type: {file_type}")
            
        model_dir = BASE_MODEL_DIR / model_type
        file_name = MODEL_PATHS[model_type][file_type]
        file_path = model_dir / file_name
        
        logger.debug(f"Resolved path for {model_type} {file_type}: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error getting model path: {str(e)}")
        raise

def ensure_model_directories() -> Dict[str, bool]:
    """
    Ensure all model directories exist.
    
    Returns:
        Dictionary mapping model types to success status
    """
    results = {}
    try:
        for model_type in MODEL_PATHS.keys():
            model_dir = BASE_MODEL_DIR / model_type
            try:
                model_dir.mkdir(parents=True, exist_ok=True)
                results[model_type] = True
                logger.info(f"Created/verified directory for {model_type}")
            except Exception as e:
                results[model_type] = False
                logger.error(f"Failed to create directory for {model_type}: {str(e)}")
                
        return results
        
    except Exception as e:
        logger.error(f"Error ensuring model directories: {str(e)}")
        raise

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
            model_file = model_dir / MODEL_PATHS[model_type]['model_file']
            config_file = model_dir / MODEL_PATHS[model_type]['config_file']
            
            results[model_type] = {
                'directory': {
                    'exists': model_dir.exists(),
                    'is_dir': model_dir.is_dir()
                },
                'model_file': {
                    'exists': model_file.exists(),
                    'is_file': model_file.is_file()
                },
                'config_file': {
                    'exists': config_file.exists(),
                    'is_file': config_file.is_file()
                }
            }
            
            logger.info(f"Verified paths for {model_type}: {results[model_type]}")
            
        return results
        
    except Exception as e:
        logger.error(f"Error verifying model paths: {str(e)}")
        raise 