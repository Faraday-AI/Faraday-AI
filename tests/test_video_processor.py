import pytest
import numpy as np
import cv2
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from app.services.physical_education.services.video_processor import VideoProcessor
from app.services.physical_education.models.movement_analysis.movement_models import MovementModels
from app.services.physical_education.models.skill_assessment.skill_models import SkillModels

@pytest.fixture
async def video_processor():
    processor = VideoProcessor()
    await processor.initialize()
    yield processor
    await processor.cleanup()

@pytest.fixture
def mock_frame():
    return np.zeros((368, 368, 3), dtype=np.uint8)

@pytest.fixture
def mock_video_url():
    return "test_video.mp4"

@pytest.mark.asyncio
async def test_initialization(video_processor):
    """Test proper initialization of VideoProcessor."""
    assert video_processor.frame_cache == {}
    assert video_processor.analysis_cache == {}
    assert video_processor.processing_config is not None
    assert isinstance(video_processor.movement_models, MovementModels)
    assert isinstance(video_processor.skill_models, SkillModels)

@pytest.mark.asyncio
async def test_process_video(video_processor, mock_video_url):
    """Test video processing functionality."""
    with patch('cv2.VideoCapture') as mock_cap:
        mock_cap.return_value.isOpened.return_value = True
        mock_cap.return_value.read.return_value = (True, np.zeros((368, 368, 3)))
        mock_cap.return_value.get.side_effect = [30.0, 300, 1280, 720]
        
        result = await video_processor.process_video(mock_video_url)
        
        assert result["status"] == "success"
        assert "video_info" in result
        assert "key_frames" in result
        assert "analysis" in result
        assert "processing_stats" in result

@pytest.mark.asyncio
async def test_process_frame(video_processor, mock_frame):
    """Test frame processing functionality."""
    with patch.object(video_processor.movement_models, 'extract_features', new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = {"test_feature": 1.0}
        
        result = await video_processor.process_frame(mock_frame)
        
        assert "key_points" in result
        assert "features" in result
        assert "timestamp" in result
        assert "quality_score" in result

@pytest.mark.asyncio
async def test_extract_features(video_processor, mock_frame):
    """Test feature extraction functionality."""
    key_points = {"point1": [0, 0], "point2": [1, 1]}
    
    with patch.object(video_processor.movement_models, 'extract_features', new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = {"test_feature": 1.0}
        
        result = await video_processor.extract_features(mock_frame, key_points)
        
        assert isinstance(result, dict)
        assert "test_feature" in result

@pytest.mark.asyncio
async def test_analyze_frames(video_processor):
    """Test frame analysis functionality."""
    test_frames = [
        {"key_points": {"point1": [0, 0]}, "features": {"feature1": 1.0}},
        {"key_points": {"point1": [1, 1]}, "features": {"feature1": 2.0}}
    ]
    
    result = await video_processor.analyze_frames(test_frames)
    
    assert isinstance(result, dict)
    assert "movement_patterns" in result
    assert "quality_metrics" in result

@pytest.mark.asyncio
async def test_quality_metrics(video_processor, mock_frame):
    """Test quality metrics calculation."""
    frames = [
        {"frame": mock_frame, "quality_score": 0.8},
        {"frame": mock_frame, "quality_score": 0.9}
    ]
    
    result = await video_processor.calculate_quality_metrics(frames)
    
    assert isinstance(result, dict)
    assert "average_quality" in result
    assert "quality_distribution" in result

@pytest.mark.asyncio
async def test_motion_analysis(video_processor):
    """Test motion analysis functionality."""
    frames = [np.zeros((368, 368, 3)) for _ in range(5)]
    
    result = await video_processor.analyze_motion(frames)
    
    assert isinstance(result, dict)
    assert "motion_vectors" in result
    assert "motion_intensity" in result

@pytest.mark.asyncio
async def test_temporal_analysis(video_processor):
    """Test temporal pattern analysis."""
    frames = [np.zeros((368, 368, 3)) for _ in range(5)]
    
    result = await video_processor.analyze_temporal_patterns(frames)
    
    assert isinstance(result, dict)
    assert "temporal_features" in result
    assert "pattern_analysis" in result

@pytest.mark.asyncio
async def test_spatial_analysis(video_processor):
    """Test spatial pattern analysis."""
    frames = [np.zeros((368, 368, 3)) for _ in range(5)]
    
    result = await video_processor.analyze_spatial_patterns(frames)
    
    assert isinstance(result, dict)
    assert "spatial_features" in result
    assert "composition_analysis" in result

@pytest.mark.asyncio
async def test_video_enhancement(video_processor):
    """Test video enhancement functionality."""
    frames = [np.zeros((368, 368, 3)) for _ in range(3)]
    settings = {
        "brightness": 1.2,
        "contrast": 1.1,
        "sharpness": 1.0
    }
    
    enhanced_frames = await video_processor.enhance_video(frames, settings)
    
    assert len(enhanced_frames) == len(frames)
    assert isinstance(enhanced_frames[0], np.ndarray)

@pytest.mark.asyncio
async def test_compression_analysis(video_processor):
    """Test compression analysis functionality."""
    frames = [np.zeros((368, 368, 3)) for _ in range(3)]
    
    result = await video_processor.analyze_compression(frames)
    
    assert isinstance(result, dict)
    assert "compression_artifacts" in result
    assert "quality_impact" in result

@pytest.mark.asyncio
async def test_artifact_detection(video_processor):
    """Test artifact detection functionality."""
    frames = [np.zeros((368, 368, 3)) for _ in range(3)]
    
    result = await video_processor.detect_artifacts(frames)
    
    assert isinstance(result, dict)
    assert "detected_artifacts" in result
    assert "severity_levels" in result

@pytest.mark.asyncio
async def test_cache_management(video_processor, mock_frame):
    """Test cache management functionality."""
    # Test frame cache
    frame_hash = hash(mock_frame.tobytes())
    processed_frame = await video_processor.process_frame(mock_frame)
    assert frame_hash in video_processor.frame_cache
    
    # Test analysis cache
    key_points = {"point1": [0, 0]}
    await video_processor.extract_features(mock_frame, key_points)
    feature_hash = hash((mock_frame.tobytes(), str(key_points)))
    assert feature_hash in video_processor.analysis_cache

@pytest.mark.asyncio
async def test_error_handling(video_processor):
    """Test error handling functionality."""
    with pytest.raises(ValueError):
        await video_processor.process_video("nonexistent_video.mp4")
    
    with pytest.raises(Exception):
        await video_processor.process_frame(None)

@pytest.mark.asyncio
async def test_performance_optimization(video_processor, mock_video_url):
    """Test performance optimization functionality."""
    result = await video_processor.optimize_processing(mock_video_url)
    
    assert isinstance(result, dict)
    assert "optimization_settings" in result
    assert "performance_metrics" in result 