# Standard library imports
import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

# Third-party imports
import cv2
import mediapipe as mp
import numpy as np
from sqlalchemy.orm import Session

# Local application imports
from app.core.database import get_db
from app.core.monitoring import track_metrics
from app.models.movement_analysis.analysis.movement_analysis import MovementAnalysis, MovementPattern
from app.models.physical_education.activity.models import Activity
from app.models.physical_education.student.models import Student
from app.models.physical_education.pe_enums.pe_types import (
    MovementType,
    AnalysisStatus,
    ConfidenceLevel
)
from app.models.physical_education.skill_assessment.skill_assessment_models import SkillModels
from app.services.physical_education.movement_analyzer import MovementAnalyzer

class VideoProcessor:
    """Service for processing video data and extracting movement information."""
    
    def __init__(self):
        self.logger = logging.getLogger("video_processor")
        self.cap = None
        self.model = None
        self.movement_models = MovementModels()
        self.skill_models = SkillModels()
        self.processing_history = []
        self.frame_cache = {}
        self.analysis_cache = {}
        self.batch_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
        self.processing_config = {
            "frame_interval": 0.5,  # seconds
            "batch_size": 32,
            "quality_threshold": 0.7,
            "max_cache_size": 1000,
            "max_batch_cache_size": 100,
            "cache_ttl": 3600,  # 1 hour in seconds
            "memory_limit": 1024 * 1024 * 1024,  # 1GB in bytes
            "batch_processing": True,
            "parallel_processing": True,
            "compression_enabled": True,
            "compression_quality": 0.9
        }
        self.video_metadata = {}
        self.quality_metrics = {}
        self.motion_analysis = {}
        self.temporal_analysis = {}
        self.spatial_analysis = {}
        self.feature_extraction = {}
        self.compression_analysis = {}
        self.artifact_detection = {}
        self.enhancement_history = {}
        self.export_settings = {}
        self.movement_analyzer = MovementAnalyzer()
        
        # Video processing settings
        self.settings = {
            "frame_rate": 30,
            "resolution": (1920, 1080),
            "quality": 0.9,
            "compression": "h264",
            "max_duration": 300,  # 5 minutes in seconds
            "min_duration": 1,    # 1 second
            "max_file_size": 1024 * 1024 * 1024,  # 1GB in bytes
            "supported_formats": [".mp4", ".avi", ".mov", ".mkv"],
            "temp_dir": "/tmp/video_processing"
        }
        
        # Processing state
        self.processing_state = {
            "active_processes": 0,
            "queued_videos": [],
            "processed_videos": [],
            "failed_videos": [],
            "current_video": None
        }
        
        # Performance metrics
        self.performance_metrics = {
            "processing_times": [],
            "memory_usage": [],
            "cpu_usage": [],
            "gpu_usage": [],
            "error_rates": {},
            "success_rates": {}
        }
        
        # Resource management
        self.resource_limits = {
            "max_concurrent_processes": 4,
            "max_memory_usage": 1024 * 1024 * 1024,  # 1GB in bytes
            "max_cpu_usage": 0.8,  # 80% CPU usage
            "max_gpu_usage": 0.8   # 80% GPU usage
        }
        
        # Cache management
        self.cache = {
            "frames": {},
            "features": {},
            "results": {}
        }
        
        # Error handling
        self.error_handling = {
            "retry_count": 3,
            "retry_delay": 5,  # seconds
            "error_threshold": 0.1,  # 10% error rate threshold
            "recovery_strategies": {}
        }
        
    async def initialize(self):
        """Initialize video processing resources."""
        try:
            # Check if model files exist
            prototxt_path = "/app/models/pose_deploy_linevec.prototxt"
            caffemodel_path = "/app/models/pose_iter_440000.caffemodel"
            
            if not os.path.exists(prototxt_path) or not os.path.exists(caffemodel_path):
                self.logger.warning("OpenCV model files not found. Video processing will be limited.")
                return
                
            # Load OpenCV models
            self.model = cv2.dnn.readNetFromCaffe(
                prototxt_path,
                caffemodel_path
            )
            
            # Initialize movement and skill models
            await self.movement_models.initialize()
            await self.skill_models.initialize()
            
            # Initialize caches and configurations
            self.frame_cache = {}
            self.analysis_cache = {}
            self.video_metadata = {}
            self.processing_config = {
                "frame_interval": 0.5,  # seconds
                "batch_size": 32,
                "quality_threshold": 0.7,
                "max_cache_size": 1000,
                "max_batch_cache_size": 100,
                "cache_ttl": 3600,  # 1 hour in seconds
                "memory_limit": 1024 * 1024 * 1024,  # 1GB in bytes
                "batch_processing": True,
                "parallel_processing": True,
                "compression_enabled": True,
                "compression_quality": 0.9
            }
            
            # Initialize movement analyzer
            await self.movement_analyzer.initialize()
            
            # Create temporary directory if it doesn't exist
            os.makedirs(self.settings["temp_dir"], exist_ok=True)
            
            # Initialize GPU if available
            self.initialize_gpu()
            
            # Initialize error recovery strategies
            self.initialize_error_recovery()
            
            self.logger.info("Video processor initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing video processor: {str(e)}")
            raise
            
    async def cleanup(self):
        """Cleanup video processing resources."""
        try:
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            await self.movement_models.cleanup()
            await self.skill_models.cleanup()
            self.frame_cache.clear()
            self.analysis_cache.clear()
            self.video_metadata.clear()
            self.motion_analysis.clear()
            self.temporal_analysis.clear()
            self.spatial_analysis.clear()
            self.feature_extraction.clear()
            self.compression_analysis.clear()
            self.artifact_detection.clear()
            self.enhancement_history.clear()
            self.export_settings.clear()
            self.logger.info("Video processor cleaned up")
            
            # Cleanup movement analyzer
            await self.movement_analyzer.cleanup()
            
            # Clear all caches
            self.clear_caches()
            
            # Remove temporary files
            self.cleanup_temp_files()
        except Exception as e:
            self.logger.error(f"Error cleaning up video processor: {str(e)}")
            raise
            
    def initialize_gpu(self):
        """Initialize GPU resources if available."""
        try:
            if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                cv2.cuda.setDevice(0)
                self.logger.info("GPU initialized successfully")
            else:
                self.logger.warning("No GPU available, using CPU")
        except Exception as e:
            self.logger.error(f"Error initializing GPU: {str(e)}")
            raise

    def initialize_error_recovery(self):
        """Initialize error recovery strategies."""
        self.error_handling["recovery_strategies"] = {
            "corrupted_frame": self.handle_corrupted_frame,
            "missing_frame": self.handle_missing_frame,
            "processing_error": self.handle_processing_error,
            "resource_exhaustion": self.handle_resource_exhaustion,
            "invalid_format": self.handle_invalid_format
        }

    @track_metrics
    async def process_video(self, video_path: str) -> Dict[str, Any]:
        """Process a video file and extract movement information."""
        try:
            # Validate video file
            if not self.validate_video(video_path):
                raise ValueError(f"Invalid video file: {video_path}")
            
            # Update processing state
            self.processing_state["current_video"] = video_path
            self.processing_state["active_processes"] += 1
            
            start_time = datetime.now()
            
            # Extract frames
            frames = await self.extract_frames(video_path)
            
            # Process frames
            processed_frames = await self.process_frames(frames)
            
            # Analyze movement
            analysis_results = await self.movement_analyzer.analyze(processed_frames)
            
            # Generate report
            report = self.generate_report(analysis_results)
            
            # Update metrics
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            self.update_performance_metrics(processing_time)
            
            # Update processing state
            self.processing_state["processed_videos"].append(video_path)
            self.processing_state["active_processes"] -= 1
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error processing video {video_path}: {str(e)}")
            self.processing_state["failed_videos"].append(video_path)
            self.processing_state["active_processes"] -= 1
            raise

    def validate_video(self, video_path: str) -> bool:
        """Validate video file format and properties."""
        try:
            # Check file existence
            if not os.path.exists(video_path):
                return False
            
            # Check file extension
            _, ext = os.path.splitext(video_path)
            if ext.lower() not in self.settings["supported_formats"]:
                return False
            
            # Check file size
            if os.path.getsize(video_path) > self.settings["max_file_size"]:
                return False
            
            # Check video properties
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False
            
            # Check duration
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps
            
            if duration < self.settings["min_duration"] or duration > self.settings["max_duration"]:
                return False
            
            cap.release()
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating video {video_path}: {str(e)}")
            return False

    async def extract_frames(self, video_path: str) -> List[np.ndarray]:
        """Extract frames from video file."""
        try:
            frames = []
            cap = cv2.VideoCapture(video_path)
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Resize frame if needed
                if frame.shape[:2] != self.settings["resolution"]:
                    frame = cv2.resize(frame, self.settings["resolution"])
                
                frames.append(frame)
            
            cap.release()
            return frames
            
        except Exception as e:
            self.logger.error(f"Error extracting frames from {video_path}: {str(e)}")
            raise

    async def process_frames(self, frames: List[np.ndarray]) -> List[Dict[str, Any]]:
        """Process extracted frames."""
        try:
            processed_frames = []
            
            for frame in frames:
                # Check cache
                frame_hash = hash(frame.tobytes())
                if frame_hash in self.cache["frames"]:
                    self.cache_stats["hits"] += 1
                    processed_frames.append(self.cache["frames"][frame_hash])
                    continue
                
                self.cache_stats["misses"] += 1
                
                # Process frame
                processed_frame = {
                    "data": frame,
                    "features": self.extract_features(frame),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Update cache
                self.cache["frames"][frame_hash] = processed_frame
                processed_frames.append(processed_frame)
                
                # Manage cache size
                await self.manage_cache()
            
            return processed_frames
            
        except Exception as e:
            self.logger.error(f"Error processing frames: {str(e)}")
            raise

    def extract_features(self, frame: np.ndarray) -> Dict[str, Any]:
        """Extract features from a single frame."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Extract edges
            edges = cv2.Canny(gray, 100, 200)
            
            # Extract keypoints
            sift = cv2.SIFT_create()
            keypoints, descriptors = sift.detectAndCompute(gray, None)
            
            # Calculate motion
            if hasattr(self, 'previous_frame'):
                flow = cv2.calcOpticalFlowFarneback(
                    self.previous_frame,
                    gray,
                    None,
                    0.5, 3, 15, 3, 5, 1.2, 0
                )
            else:
                flow = None
            
            self.previous_frame = gray
            
            return {
                "edges": edges,
                "keypoints": keypoints,
                "descriptors": descriptors,
                "flow": flow
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting features: {str(e)}")
            raise

    async def manage_cache(self):
        """Manage cache size and memory usage."""
        try:
            # Check memory usage
            if self._estimate_memory_usage() > self.resource_limits["max_memory_usage"]:
                self.clear_caches()
                return
            
            # Remove oldest entries if cache is too large
            max_entries = 1000
            for cache_type in self.cache:
                if len(self.cache[cache_type]) > max_entries:
                    oldest_keys = sorted(
                        self.cache[cache_type].keys(),
                        key=lambda k: self.cache[cache_type][k].get("timestamp", "")
                    )[:len(self.cache[cache_type]) - max_entries]
                    
                    for key in oldest_keys:
                        del self.cache[cache_type][key]
                        self.cache_stats["evictions"] += 1
                        
        except Exception as e:
            self.logger.error(f"Error managing cache: {str(e)}")
            raise

    def _estimate_memory_usage(self) -> int:
        """Estimate current memory usage."""
        try:
            import sys
            
            total_size = 0
            for cache_type in self.cache:
                for item in self.cache[cache_type].values():
                    total_size += sys.getsizeof(item)
            
            return total_size
            
        except Exception as e:
            self.logger.error(f"Error estimating memory usage: {str(e)}")
            return 0

    def clear_caches(self):
        """Clear all caches."""
        try:
            for cache_type in self.cache:
                self.cache[cache_type].clear()
            
            self.cache_stats = {
                "hits": 0,
                "misses": 0,
                "evictions": 0
            }
            
            self.logger.info("All caches cleared")
        except Exception as e:
            self.logger.error(f"Error clearing caches: {str(e)}")

    def cleanup_temp_files(self):
        """Clean up temporary files."""
        try:
            import shutil
            shutil.rmtree(self.settings["temp_dir"], ignore_errors=True)
            os.makedirs(self.settings["temp_dir"], exist_ok=True)
            self.logger.info("Temporary files cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up temporary files: {str(e)}")

    def update_performance_metrics(self, processing_time: float):
        """Update performance metrics."""
        try:
            self.performance_metrics["processing_times"].append(processing_time)
            
            # Update success rate
            total_videos = len(self.processing_state["processed_videos"]) + len(self.processing_state["failed_videos"])
            if total_videos > 0:
                success_rate = len(self.processing_state["processed_videos"]) / total_videos
                self.performance_metrics["success_rates"]["overall"] = success_rate
            
            # Update error rate
            if total_videos > 0:
                error_rate = len(self.processing_state["failed_videos"]) / total_videos
                self.performance_metrics["error_rates"]["overall"] = error_rate
            
            # Trim metrics history if too long
            max_history = 1000
            if len(self.performance_metrics["processing_times"]) > max_history:
                self.performance_metrics["processing_times"] = self.performance_metrics["processing_times"][-max_history:]
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {str(e)}")

    def generate_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report from analysis results."""
        try:
            return {
                "analysis_results": analysis_results,
                "performance_metrics": {
                    "processing_time": np.mean(self.performance_metrics["processing_times"]),
                    "success_rate": self.performance_metrics["success_rates"].get("overall", 0),
                    "error_rate": self.performance_metrics["error_rates"].get("overall", 0)
                },
                "cache_stats": self.cache_stats,
                "resource_usage": {
                    "memory": self._estimate_memory_usage(),
                    "active_processes": self.processing_state["active_processes"]
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise

    # Error handling methods
    async def handle_corrupted_frame(self, frame_index: int) -> Optional[np.ndarray]:
        """Handle corrupted frame."""
        try:
            if frame_index > 0 and hasattr(self, 'previous_frame'):
                return self.previous_frame
            return None
        except Exception as e:
            self.logger.error(f"Error handling corrupted frame: {str(e)}")
            return None

    async def handle_missing_frame(self, frame_index: int) -> Optional[np.ndarray]:
        """Handle missing frame."""
        try:
            if frame_index > 0 and hasattr(self, 'previous_frame'):
                return self.previous_frame
            return None
        except Exception as e:
            self.logger.error(f"Error handling missing frame: {str(e)}")
            return None

    async def handle_processing_error(self, error: Exception) -> bool:
        """Handle processing error."""
        try:
            self.logger.error(f"Processing error: {str(error)}")
            return False
        except Exception as e:
            self.logger.error(f"Error handling processing error: {str(e)}")
            return False

    async def handle_resource_exhaustion(self) -> bool:
        """Handle resource exhaustion."""
        try:
            self.clear_caches()
            return True
        except Exception as e:
            self.logger.error(f"Error handling resource exhaustion: {str(e)}")
            return False

    async def handle_invalid_format(self, video_path: str) -> bool:
        """Handle invalid video format."""
        try:
            self.logger.error(f"Invalid video format: {video_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error handling invalid format: {str(e)}")
            return False

    @track_metrics
    async def process_video_old(self, video_url: str) -> Dict[str, Any]:
        """Process video and extract key frames and features."""
        try:
            if not self.model:
                self.logger.warning("Video processing model not available. Returning basic video information.")
                return {
                    "status": "success",
                    "message": "Video processing model not available",
                    "basic_info": {
                        "url": video_url
                    }
                }
                
            self.cap = cv2.VideoCapture(video_url)
            if not self.cap.isOpened():
                raise ValueError(f"Could not open video: {video_url}")
                
            # Get video properties
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Store video metadata
            self.video_metadata[video_url] = {
                "fps": fps,
                "frame_count": frame_count,
                "duration": duration,
                "resolution": f"{width}x{height}",
                "timestamp": datetime.now().isoformat()
            }
            
            # Process frames
            frames = []
            key_frames = []
            frame_interval = int(fps * self.processing_config["frame_interval"])
            
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break
                    
                if len(frames) % frame_interval == 0:
                    processed_frame = await self.process_frame(frame)
                    if await self.assess_frame_quality(processed_frame):
                        key_frames.append(processed_frame)
                    
                frames.append(frame)
                
            # Store processing history
            self.processing_history.append({
                "timestamp": datetime.now().isoformat(),
                "video_url": video_url,
                "frame_count": frame_count,
                "duration": duration,
                "key_frames": len(key_frames),
                "processing_time": self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            })
                
            return {
                "status": "success",
                "video_info": {
                    "fps": fps,
                    "frame_count": frame_count,
                    "duration": duration,
                    "resolution": f"{width}x{height}"
                },
                "key_frames": key_frames,
                "analysis": await self.analyze_frames(key_frames),
                "processing_stats": {
                    "total_frames_processed": len(frames),
                    "key_frames_extracted": len(key_frames),
                    "processing_time": self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0,
                    "quality_metrics": await self.calculate_quality_metrics(key_frames)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error processing video: {str(e)}")
            raise
            
    async def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Process a single frame and extract features."""
        try:
            # Check cache first
            frame_hash = hash(frame.tobytes())
            if frame_hash in self.frame_cache:
                return self.frame_cache[frame_hash]
            
            # Resize frame for processing
            blob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (368, 368),
                                      (0, 0, 0), swapRB=False, crop=False)
            
            # Get pose estimation
            self.model.setInput(blob)
            output = self.model.forward()
            
            # Extract key points
            key_points = self.extract_key_points(output)
            
            # Extract features
            features = await self.extract_features(frame, key_points)
            
            # Store in cache
            processed_frame = {
                "key_points": key_points,
                "features": features,
                "timestamp": self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0,
                "quality_score": await self.calculate_frame_quality(frame, key_points)
            }
            
            self.frame_cache[frame_hash] = processed_frame
            return processed_frame
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {str(e)}")
            raise
            
    def extract_key_points(self, output: np.ndarray) -> Dict[str, Any]:
        """Extract key points from pose estimation output."""
        try:
            return self.movement_models.extract_key_points(output)
        except Exception as e:
            self.logger.error(f"Error extracting key points: {str(e)}")
            raise
        
    async def extract_features(self, frame: np.ndarray, key_points: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional features from frame and key points."""
        try:
            # Check cache first
            feature_hash = hash((frame.tobytes(), str(key_points)))
            if feature_hash in self.analysis_cache:
                return self.analysis_cache[feature_hash]
            
            features = await self.movement_models.extract_features(frame, key_points)
            
            # Store in cache
            self.analysis_cache[feature_hash] = features
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting features: {str(e)}")
            raise
        
    async def analyze_frames(self, frames: list) -> Dict[str, Any]:
        """Analyze sequence of frames for movement patterns."""
        try:
            # Check cache first
            frames_hash = hash(str([frame["key_points"] for frame in frames]))
            if frames_hash in self.analysis_cache:
                return self.analysis_cache[frames_hash]
            
            movement_patterns = []
            for i in range(len(frames) - 1):
                pattern = await self.compare_frames(frames[i], frames[i + 1])
                movement_patterns.append(pattern)
                
            analysis = {
                "movement_patterns": movement_patterns,
                "summary": await self.summarize_movements(movement_patterns),
                "skill_assessment": await self.skill_models.assess_skills(movement_patterns),
                "movement_quality": await self.assess_movement_quality(movement_patterns),
                "performance_metrics": await self.calculate_performance_metrics(movement_patterns),
                "safety_assessment": await self.assess_safety(movement_patterns)
            }
            
            # Store in cache
            self.analysis_cache[frames_hash] = analysis
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing frames: {str(e)}")
            raise
            
    async def compare_frames(self, frame1: Dict[str, Any], frame2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two frames to detect movement."""
        try:
            return await self.movement_models.compare_frames(frame1, frame2)
        except Exception as e:
            self.logger.error(f"Error comparing frames: {str(e)}")
            raise
        
    async def summarize_movements(self, patterns: list) -> Dict[str, Any]:
        """Summarize detected movement patterns."""
        try:
            return await self.movement_models.summarize_movements(patterns)
        except Exception as e:
            self.logger.error(f"Error summarizing movements: {str(e)}")
            raise
            
    async def assess_movement_quality(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the quality of movements."""
        try:
            return await self.movement_models.assess_movement_quality(patterns)
        except Exception as e:
            self.logger.error(f"Error assessing movement quality: {str(e)}")
            raise
            
    async def calculate_performance_metrics(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance-related metrics."""
        try:
            return await self.movement_models.calculate_performance_metrics(patterns)
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {str(e)}")
            raise
            
    async def assess_safety(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess movement safety and risk factors."""
        try:
            return await self.movement_models.assess_safety(patterns)
        except Exception as e:
            self.logger.error(f"Error assessing safety: {str(e)}")
            raise
            
    async def assess_frame_quality(self, processed_frame: Dict[str, Any]) -> bool:
        """Assess if frame quality meets threshold."""
        try:
            quality_score = processed_frame.get("quality_score", 0)
            return quality_score >= self.processing_config["quality_threshold"]
        except Exception as e:
            self.logger.error(f"Error assessing frame quality: {str(e)}")
            return False
            
    async def calculate_frame_quality(self, frame: np.ndarray, key_points: Dict[str, Any]) -> float:
        """Calculate quality score for a frame."""
        try:
            return await self.movement_models.calculate_frame_quality(frame, key_points)
        except Exception as e:
            self.logger.error(f"Error calculating frame quality: {str(e)}")
            return 0.0
            
    async def calculate_quality_metrics(self, frames: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate quality metrics for a set of frames."""
        try:
            return {
                "average_quality": np.mean([f.get("quality_score", 0) for f in frames]),
                "min_quality": min([f.get("quality_score", 0) for f in frames]),
                "max_quality": max([f.get("quality_score", 0) for f in frames]),
                "quality_distribution": await self.analyze_quality_distribution(frames)
            }
        except Exception as e:
            self.logger.error(f"Error calculating quality metrics: {str(e)}")
            raise
            
    async def analyze_quality_distribution(self, frames: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of quality scores."""
        try:
            scores = [f.get("quality_score", 0) for f in frames]
            return {
                "histogram": np.histogram(scores, bins=10)[0].tolist(),
                "percentiles": {
                    "25th": np.percentile(scores, 25),
                    "50th": np.percentile(scores, 50),
                    "75th": np.percentile(scores, 75)
                }
            }
        except Exception as e:
            self.logger.error(f"Error analyzing quality distribution: {str(e)}")
            raise
            
    async def optimize_processing(self, video_url: str) -> Dict[str, Any]:
        """Optimize video processing parameters based on video characteristics."""
        try:
            self.cap = cv2.VideoCapture(video_url)
            if not self.cap.isOpened():
                raise ValueError(f"Could not open video: {video_url}")
                
            # Analyze video characteristics
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Determine optimal processing parameters
            optimal_interval = max(1, int(fps * 0.5))  # Process every 0.5 seconds
            batch_size = min(32, max(8, int(frame_count / 100)))  # Adaptive batch size
            
            # Update processing configuration
            self.processing_config.update({
                "frame_interval": optimal_interval / fps,
                "batch_size": batch_size,
                "quality_threshold": 0.7,
                "max_cache_size": min(1000, frame_count)
            })
            
            return {
                "status": "success",
                "optimization": {
                    "frame_interval": optimal_interval,
                    "batch_size": batch_size,
                    "estimated_processing_time": duration / optimal_interval,
                    "memory_usage": batch_size * width * height * 3,  # Approximate memory usage
                    "quality_threshold": self.processing_config["quality_threshold"],
                    "max_cache_size": self.processing_config["max_cache_size"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing processing: {str(e)}")
            raise
            
    async def get_processing_history(self) -> List[Dict[str, Any]]:
        """Get history of video processing operations."""
        return self.processing_history
        
    async def clear_cache(self):
        """Clear the frame and analysis cache."""
        self.frame_cache.clear()
        self.analysis_cache.clear()
        self.logger.info("Cache cleared successfully")
        
    async def get_video_metadata(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific video."""
        return self.video_metadata.get(video_url)
        
    async def get_processing_config(self) -> Dict[str, Any]:
        """Get current processing configuration."""
        return self.processing_config
        
    async def update_processing_config(self, config: Dict[str, Any]):
        """Update processing configuration."""
        try:
            self.processing_config.update(config)
            self.logger.info("Processing configuration updated successfully")
        except Exception as e:
            self.logger.error(f"Error updating processing configuration: {str(e)}")
            raise
            
    async def analyze_video_quality(self, video_url: str) -> Dict[str, Any]:
        """Analyze overall video quality."""
        try:
            self.cap = cv2.VideoCapture(video_url)
            if not self.cap.isOpened():
                raise ValueError(f"Could not open video: {video_url}")
                
            # Sample frames for quality analysis
            sample_frames = []
            frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_indices = np.linspace(0, frame_count-1, 10, dtype=int)
            
            for i in range(frame_count):
                ret, frame = self.cap.read()
                if not ret:
                    break
                if i in sample_indices:
                    sample_frames.append(frame)
                    
            # Analyze quality metrics
            quality_metrics = {
                "resolution": {
                    "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                },
                "fps": self.cap.get(cv2.CAP_PROP_FPS),
                "brightness": await self.analyze_brightness(sample_frames),
                "contrast": await self.analyze_contrast(sample_frames),
                "sharpness": await self.analyze_sharpness(sample_frames),
                "noise": await self.analyze_noise(sample_frames),
                "stability": await self.analyze_stability(sample_frames)
            }
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Error analyzing video quality: {str(e)}")
            raise
            
    async def analyze_brightness(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze brightness levels in frames."""
        try:
            brightness_values = [np.mean(frame) for frame in frames]
            return {
                "mean": np.mean(brightness_values),
                "std": np.std(brightness_values),
                "min": np.min(brightness_values),
                "max": np.max(brightness_values)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing brightness: {str(e)}")
            raise
            
    async def analyze_contrast(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze contrast levels in frames."""
        try:
            contrast_values = [np.std(frame) for frame in frames]
            return {
                "mean": np.mean(contrast_values),
                "std": np.std(contrast_values),
                "min": np.min(contrast_values),
                "max": np.max(contrast_values)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing contrast: {str(e)}")
            raise
            
    async def analyze_sharpness(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze sharpness levels in frames."""
        try:
            sharpness_values = [cv2.Laplacian(frame, cv2.CV_64F).var() for frame in frames]
            return {
                "mean": np.mean(sharpness_values),
                "std": np.std(sharpness_values),
                "min": np.min(sharpness_values),
                "max": np.max(sharpness_values)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing sharpness: {str(e)}")
            raise
            
    async def analyze_noise(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze noise levels in frames."""
        try:
            noise_values = [np.std(frame - cv2.GaussianBlur(frame, (5,5), 0)) for frame in frames]
            return {
                "mean": np.mean(noise_values),
                "std": np.std(noise_values),
                "min": np.min(noise_values),
                "max": np.max(noise_values)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing noise: {str(e)}")
            raise
            
    async def analyze_stability(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze video stability."""
        try:
            # Calculate optical flow between consecutive frames
            flow_values = []
            prev_frame = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
            
            for frame in frames[1:]:
                curr_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                flow = cv2.calcOpticalFlowFarneback(prev_frame, curr_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                flow_values.append(np.mean(magnitude))
                prev_frame = curr_frame
                
            return {
                "mean_flow": np.mean(flow_values),
                "std_flow": np.std(flow_values),
                "max_flow": np.max(flow_values),
                "stability_score": 1.0 / (1.0 + np.mean(flow_values))  # Higher score means more stable
            }
        except Exception as e:
            self.logger.error(f"Error analyzing stability: {str(e)}")
            raise
            
    async def analyze_motion(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze motion patterns in video frames."""
        try:
            motion_metrics = {
                "optical_flow": await self.calculate_optical_flow(frames),
                "motion_vectors": await self.extract_motion_vectors(frames),
                "motion_consistency": await self.analyze_motion_consistency(frames),
                "motion_quality": await self.assess_motion_quality(frames)
            }
            
            self.motion_analysis[frames[0].tobytes()] = motion_metrics
            return motion_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing motion: {str(e)}")
            raise
            
    async def calculate_optical_flow(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Calculate optical flow between frames."""
        try:
            flow_values = []
            prev_frame = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
            
            for frame in frames[1:]:
                curr_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                flow = cv2.calcOpticalFlowFarneback(prev_frame, curr_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                flow_values.append({
                    "mean": np.mean(magnitude),
                    "std": np.std(magnitude),
                    "max": np.max(magnitude),
                    "direction": np.mean(np.arctan2(flow[..., 1], flow[..., 0]))
                })
                prev_frame = curr_frame
                
            return {
                "mean_flow": np.mean([f["mean"] for f in flow_values]),
                "std_flow": np.std([f["mean"] for f in flow_values]),
                "max_flow": max([f["max"] for f in flow_values]),
                "direction_consistency": await self.analyze_direction_consistency([f["direction"] for f in flow_values])
            }
        except Exception as e:
            self.logger.error(f"Error calculating optical flow: {str(e)}")
            raise
            
    async def extract_motion_vectors(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Extract motion vectors from frames."""
        try:
            vectors = []
            prev_frame = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
            
            for frame in frames[1:]:
                curr_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                flow = cv2.calcOpticalFlowFarneback(prev_frame, curr_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                
                # Sample vectors at regular intervals
                h, w = flow.shape[:2]
                step = 16
                y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1).astype(int)
                fx, fy = flow[y,x].T
                
                vectors.append({
                    "x": fx.tolist(),
                    "y": fy.tolist(),
                    "magnitude": np.sqrt(fx**2 + fy**2).tolist(),
                    "direction": np.arctan2(fy, fx).tolist()
                })
                prev_frame = curr_frame
                
            return {
                "vectors": vectors,
                "statistics": {
                    "mean_magnitude": np.mean([np.mean(v["magnitude"]) for v in vectors]),
                    "std_magnitude": np.std([np.mean(v["magnitude"]) for v in vectors]),
                    "direction_distribution": await self.analyze_direction_distribution(vectors)
                }
            }
        except Exception as e:
            self.logger.error(f"Error extracting motion vectors: {str(e)}")
            raise
            
    async def analyze_temporal_patterns(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze temporal patterns in video frames."""
        try:
            temporal_metrics = {
                "frame_rate_consistency": await self.analyze_frame_rate_consistency(frames),
                "motion_rhythm": await self.analyze_motion_rhythm(frames),
                "temporal_smoothness": await self.analyze_temporal_smoothness(frames),
                "event_detection": await self.detect_events(frames)
            }
            
            self.temporal_analysis[frames[0].tobytes()] = temporal_metrics
            return temporal_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing temporal patterns: {str(e)}")
            raise
            
    async def analyze_spatial_patterns(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze spatial patterns in video frames."""
        try:
            spatial_metrics = {
                "composition": await self.analyze_frame_composition(frames),
                "depth_analysis": await self.analyze_depth(frames),
                "spatial_distribution": await self.analyze_spatial_distribution(frames),
                "region_of_interest": await self.detect_regions_of_interest(frames)
            }
            
            self.spatial_analysis[frames[0].tobytes()] = spatial_metrics
            return spatial_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing spatial patterns: {str(e)}")
            raise
            
    async def enhance_video(self, frames: List[np.ndarray], settings: Optional[Dict[str, Any]] = None) -> List[np.ndarray]:
        """Enhance video frames based on settings."""
        try:
            if settings is None:
                settings = self.processing_config["enhancement_settings"]
                
            enhanced_frames = []
            for frame in frames:
                # Apply brightness and contrast
                frame = cv2.convertScaleAbs(frame, alpha=settings["contrast"], beta=settings["brightness"] * 255 - 255)
                
                # Apply sharpness
                if settings["sharpness"] != 1.0:
                    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                    frame = cv2.filter2D(frame, -1, kernel * settings["sharpness"])
                    
                # Apply denoising
                if settings["denoise"]:
                    frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
                    
                enhanced_frames.append(frame)
                
            # Store enhancement history
            self.enhancement_history[frames[0].tobytes()] = {
                "settings": settings,
                "timestamp": datetime.now().isoformat(),
                "frame_count": len(frames)
            }
            
            return enhanced_frames
        except Exception as e:
            self.logger.error(f"Error enhancing video: {str(e)}")
            raise
            
    async def export_video(self, frames: List[np.ndarray], output_path: str, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export processed video with specified settings."""
        try:
            if settings is None:
                settings = self.processing_config["export_settings"]
                
            # Get video properties
            height, width = frames[0].shape[:2]
            fps = 30  # Default frame rate
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Write frames
            for frame in frames:
                out.write(frame)
                
            out.release()
            
            # Store export settings
            self.export_settings[output_path] = {
                "settings": settings,
                "timestamp": datetime.now().isoformat(),
                "frame_count": len(frames),
                "resolution": f"{width}x{height}",
                "fps": fps
            }
            
            return {
                "status": "success",
                "output_path": output_path,
                "settings": settings,
                "frame_count": len(frames),
                "resolution": f"{width}x{height}",
                "fps": fps
            }
        except Exception as e:
            self.logger.error(f"Error exporting video: {str(e)}")
            raise
            
    async def analyze_compression(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze video compression artifacts."""
        try:
            compression_metrics = {
                "blocking_artifacts": await self.detect_blocking_artifacts(frames),
                "ringing_artifacts": await self.detect_ringing_artifacts(frames),
                "banding_artifacts": await self.detect_banding_artifacts(frames),
                "compression_quality": await self.assess_compression_quality(frames)
            }
            
            self.compression_analysis[frames[0].tobytes()] = compression_metrics
            return compression_metrics
        except Exception as e:
            self.logger.error(f"Error analyzing compression: {str(e)}")
            raise
            
    async def detect_artifacts(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Detect various video artifacts."""
        try:
            artifacts = {
                "compression_artifacts": await self.analyze_compression(frames),
                "noise_artifacts": await self.detect_noise_artifacts(frames),
                "blur_artifacts": await self.detect_blur_artifacts(frames),
                "exposure_artifacts": await self.detect_exposure_artifacts(frames)
            }
            
            self.artifact_detection[frames[0].tobytes()] = artifacts
            return artifacts
        except Exception as e:
            self.logger.error(f"Error detecting artifacts: {str(e)}")
            raise
            
    async def get_enhancement_history(self) -> Dict[str, Any]:
        """Get history of video enhancement operations."""
        return self.enhancement_history
        
    async def get_export_settings(self) -> Dict[str, Any]:
        """Get history of video export settings."""
        return self.export_settings
        
    async def update_enhancement_settings(self, settings: Dict[str, Any]):
        """Update video enhancement settings."""
        try:
            self.processing_config["enhancement_settings"].update(settings)
            self.logger.info("Enhancement settings updated successfully")
        except Exception as e:
            self.logger.error(f"Error updating enhancement settings: {str(e)}")
            raise
            
    async def update_export_settings(self, settings: Dict[str, Any]):
        """Update video export settings."""
        try:
            self.processing_config["export_settings"].update(settings)
            self.logger.info("Export settings updated successfully")
        except Exception as e:
            self.logger.error(f"Error updating export settings: {str(e)}")
            raise

    async def process_frames_batch(self, frames: List[np.ndarray]) -> List[Dict[str, Any]]:
        """Process multiple frames in a batch for better performance."""
        try:
            batch_hash = hash(tuple(frame.tobytes() for frame in frames))
            
            # Check batch cache
            if batch_hash in self.batch_cache:
                self.cache_stats["hits"] += 1
                return self.batch_cache[batch_hash]
                
            self.cache_stats["misses"] += 1
            
            # Prepare batch input
            batch_blob = np.concatenate([
                cv2.dnn.blobFromImage(frame, 1.0 / 255, (368, 368), (0, 0, 0), swapRB=False, crop=False)
                for frame in frames
            ])
            
            # Process batch
            self.model.setInput(batch_blob)
            batch_output = self.model.forward()
            
            # Process results
            results = []
            for i, frame in enumerate(frames):
                output = batch_output[i:i+1]
                key_points = self.extract_key_points(output)
                features = await self.extract_features(frame, key_points)
                
                processed_frame = {
                    "key_points": key_points,
                    "features": features,
                    "timestamp": datetime.now().isoformat(),
                    "quality_score": await self.calculate_frame_quality(frame, key_points)
                }
                results.append(processed_frame)
            
            # Update batch cache
            await self.manage_batch_cache()
            self.batch_cache[batch_hash] = results
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing frame batch: {str(e)}")
            raise

    async def manage_frame_cache(self):
        """Manage frame cache size and memory usage."""
        try:
            current_size = len(self.frame_cache)
            if current_size > self.processing_config["max_cache_size"]:
                # Remove oldest entries
                items = sorted(self.frame_cache.items(), key=lambda x: x[1]["timestamp"])
                items_to_remove = items[:current_size - self.processing_config["max_cache_size"]]
                
                for key, _ in items_to_remove:
                    del self.frame_cache[key]
                    self.cache_stats["evictions"] += 1
                
            # Remove expired entries
            current_time = datetime.now().timestamp()
            expired_keys = [
                k for k, v in self.frame_cache.items()
                if (current_time - datetime.fromisoformat(v["timestamp"]).timestamp()) > self.processing_config["cache_ttl"]
            ]
            
            for key in expired_keys:
                del self.frame_cache[key]
                self.cache_stats["evictions"] += 1
                
        except Exception as e:
            self.logger.error(f"Error managing frame cache: {str(e)}")

    async def manage_batch_cache(self):
        """Manage batch cache size and memory usage."""
        try:
            current_size = len(self.batch_cache)
            if current_size > self.processing_config["max_batch_cache_size"]:
                # Remove oldest entries
                items = sorted(self.batch_cache.items(), key=lambda x: x[0])
                items_to_remove = items[:current_size - self.processing_config["max_batch_cache_size"]]
                
                for key, _ in items_to_remove:
                    del self.batch_cache[key]
                    self.cache_stats["evictions"] += 1
                    
        except Exception as e:
            self.logger.error(f"Error managing batch cache: {str(e)}")

    async def optimize_memory_usage(self):
        """Optimize memory usage by compressing cached data."""
        try:
            if not self.processing_config["compression_enabled"]:
                return
                
            # Compress frame data in cache
            for key, value in self.frame_cache.items():
                if "frame" in value and not isinstance(value["frame"], bytes):
                    _, encoded = cv2.imencode(
                        ".jpg",
                        value["frame"],
                        [cv2.IMWRITE_JPEG_QUALITY, int(self.processing_config["compression_quality"] * 100)]
                    )
                    value["frame"] = encoded.tobytes()
                    
            # Compress batch data
            for key, batch in self.batch_cache.items():
                for frame_data in batch:
                    if "frame" in frame_data and not isinstance(frame_data["frame"], bytes):
                        _, encoded = cv2.imencode(
                            ".jpg",
                            frame_data["frame"],
                            [cv2.IMWRITE_JPEG_QUALITY, int(self.processing_config["compression_quality"] * 100)]
                        )
                        frame_data["frame"] = encoded.tobytes()
                        
        except Exception as e:
            self.logger.error(f"Error optimizing memory usage: {str(e)}")

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        try:
            total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
            hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0
            
            return {
                "hits": self.cache_stats["hits"],
                "misses": self.cache_stats["misses"],
                "evictions": self.cache_stats["evictions"],
                "hit_rate": hit_rate,
                "frame_cache_size": len(self.frame_cache),
                "batch_cache_size": len(self.batch_cache),
                "memory_usage": self._estimate_memory_usage()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {str(e)}")
            raise

    def _estimate_memory_usage(self) -> int:
        """Estimate current memory usage of caches."""
        try:
            import sys
            
            frame_cache_size = sum(sys.getsizeof(v) for v in self.frame_cache.values())
            batch_cache_size = sum(
                sum(sys.getsizeof(f) for f in batch)
                for batch in self.batch_cache.values()
            )
            
            return frame_cache_size + batch_cache_size
            
        except Exception as e:
            self.logger.error(f"Error estimating memory usage: {str(e)}")
            return 0 