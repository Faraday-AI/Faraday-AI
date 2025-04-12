import pytest
from pathlib import Path
from app.services.physical_education.config.model_paths import (
    get_model_path,
    ensure_model_directories,
    verify_model_paths,
    MODEL_PATHS
)

@pytest.fixture
def temp_model_dir(tmp_path):
    """Create a temporary model directory for testing."""
    base_dir = tmp_path / "models"
    base_dir.mkdir()
    return base_dir

def test_get_model_path_valid_input(temp_model_dir, monkeypatch):
    """Test getting model path with valid input."""
    # Set the base directory to the temporary directory
    monkeypatch.setattr('app.services.physical_education.config.model_paths.BASE_MODEL_DIR', temp_model_dir)
    
    # Test each model type
    for model_type in MODEL_PATHS.keys():
        # Test model file path
        model_path = get_model_path(model_type, 'model_file')
        assert model_path.exists()
        assert model_path.parent == temp_model_dir / model_type
        
        # Test config file path
        config_path = get_model_path(model_type, 'config_file')
        assert config_path.exists()
        assert config_path.parent == temp_model_dir / model_type

def test_get_model_path_invalid_input(temp_model_dir, monkeypatch):
    """Test getting model path with invalid input."""
    # Set the base directory to the temporary directory
    monkeypatch.setattr('app.services.physical_education.config.model_paths.BASE_MODEL_DIR', temp_model_dir)
    
    # Test invalid model type
    with pytest.raises(ValueError):
        get_model_path('invalid_model_type')
    
    # Test invalid file type
    with pytest.raises(ValueError):
        get_model_path('activity_adaptation', 'invalid_file_type')

def test_ensure_model_directories(temp_model_dir, monkeypatch):
    """Test ensuring model directories exist."""
    # Set the base directory to the temporary directory
    monkeypatch.setattr('app.services.physical_education.config.model_paths.BASE_MODEL_DIR', temp_model_dir)
    
    # Ensure directories
    results = ensure_model_directories()
    
    # Verify all directories were created successfully
    assert all(results.values())
    for model_type in MODEL_PATHS.keys():
        assert (temp_model_dir / model_type).exists()
        assert (temp_model_dir / model_type).is_dir()

def test_verify_model_paths(temp_model_dir, monkeypatch):
    """Test verifying model paths."""
    # Set the base directory to the temporary directory
    monkeypatch.setattr('app.services.physical_education.config.model_paths.BASE_MODEL_DIR', temp_model_dir)
    
    # Create directories and files
    ensure_model_directories()
    for model_type in MODEL_PATHS.keys():
        model_dir = temp_model_dir / model_type
        (model_dir / MODEL_PATHS[model_type]['model_file']).touch()
        (model_dir / MODEL_PATHS[model_type]['config_file']).touch()
    
    # Verify paths
    results = verify_model_paths()
    
    # Check results
    for model_type in MODEL_PATHS.keys():
        assert results[model_type]['directory']['exists']
        assert results[model_type]['directory']['is_dir']
        assert results[model_type]['model_file']['exists']
        assert results[model_type]['model_file']['is_file']
        assert results[model_type]['config_file']['exists']
        assert results[model_type]['config_file']['is_file'] 