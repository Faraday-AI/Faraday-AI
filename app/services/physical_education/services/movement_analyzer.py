import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
from app.core.monitoring import track_metrics
import asyncio
import os
from datetime import datetime, timedelta
from app.services.physical_education.models.movement_analysis.movement_models import MovementModels
from app.services.physical_education.models.skill_assessment.skill_assessment_models import SkillModels

class MovementAnalyzer:
    """Service for analyzing movement patterns and providing feedback."""
    
    def __init__(self):
        self.logger = logging.getLogger("movement_analyzer")
        self.total_analyses = 0
        self.analysis_times = []
        self.movement_models = MovementModels()
        self.skill_models = SkillModels()
        
        # Analysis history and tracking
        self.analysis_history = []
        self.performance_benchmarks = {}
        self.injury_risk_factors = {}
        self.movement_patterns = {}
        self.feedback_history = {}
        self.progress_tracking = {}
        
        # Analysis components
        self.custom_metrics = {}
        self.environmental_factors = {}
        self.equipment_usage = {}
        self.fatigue_analysis = {}
        self.technique_variations = {}
        self.movement_consistency = {}
        self.biomechanical_analysis = {}
        self.energy_efficiency = {}
        self.symmetry_analysis = {}
        self.skill_level_assessment = {}
        self.recovery_analysis = {}
        self.adaptation_analysis = {}
        self.performance_prediction = {}
        
        # Caching and optimization
        self.analysis_cache = {}
        self.batch_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
        
        # Configuration
        self.optimization_config = {
            "max_cache_size": 1000,
            "max_batch_size": 50,
            "cache_ttl": 3600,  # 1 hour in seconds
            "memory_limit": 1024 * 1024 * 1024,  # 1GB in bytes
            "batch_processing": True,
            "parallel_processing": True,
            "compression_level": 1
        }
        
        # Performance monitoring
        self.performance_metrics = {
            'processing_times': [],
            'memory_usage': [],
            'cache_efficiency': 0.0
        }
        
        # Adaptive learning
        self.adaptive_learning = {
            'pattern_recognition': {},
            'performance_trends': {},
            'error_recovery': {}
        }
        
        # Real-time monitoring
        self.real_time_monitoring = {
            'active_sessions': 0,
            'resource_usage': {
                'cpu_usage': [],
                'memory_usage': [],
                'gpu_usage': []
            },
            'error_rates': {}
        }

    async def initialize(self):
        """Initialize movement analysis resources."""
        try:
            # Load configurations
            await self.load_performance_benchmarks()
            await self.load_injury_risk_factors()
            await self.load_custom_metrics()
            await self.load_environmental_factors()
            await self.load_equipment_usage()
            
            # Initialize monitoring
            self.initialize_adaptive_learning()
            self.initialize_real_time_monitoring()
            
            self.logger.info("Movement analyzer initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing movement analyzer: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup movement analysis resources."""
        try:
            await self.movement_models.cleanup()
            await self.skill_models.cleanup()
            
            # Clear all caches and history
            self.clear_all_data()
            self.logger.info("Movement analyzer cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up movement analyzer: {str(e)}")
            raise

    def clear_all_data(self):
        """Clear all cached data and history."""
        self.analysis_history.clear()
        self.performance_benchmarks.clear()
        self.injury_risk_factors.clear()
        self.movement_patterns.clear()
        self.feedback_history.clear()
        self.progress_tracking.clear()
        self.custom_metrics.clear()
        self.environmental_factors.clear()
        self.equipment_usage.clear()
        self.fatigue_analysis.clear()
        self.technique_variations.clear()
        self.movement_consistency.clear()
        self.biomechanical_analysis.clear()
        self.energy_efficiency.clear()
        self.symmetry_analysis.clear()
        self.skill_level_assessment.clear()
        self.recovery_analysis.clear()
        self.adaptation_analysis.clear()
        self.performance_prediction.clear()
        self.clear_caches()

    async def load_performance_benchmarks(self):
        """Load performance benchmarks for different movements."""
        try:
            self.performance_benchmarks = {
                "throwing": {
                    "velocity": {"excellent": 30.0, "good": 25.0, "average": 20.0},
                    "accuracy": {"excellent": 0.9, "good": 0.8, "average": 0.7},
                    "form_score": {"excellent": 0.9, "good": 0.8, "average": 0.7}
                },
                "jumping": {
                    "height": {"excellent": 0.6, "good": 0.5, "average": 0.4},
                    "power": {"excellent": 2000, "good": 1800, "average": 1600},
                    "form_score": {"excellent": 0.9, "good": 0.8, "average": 0.7}
                }
            }
        except Exception as e:
            self.logger.error(f"Error loading performance benchmarks: {str(e)}")
            raise

    async def load_injury_risk_factors(self):
        """Load injury risk factors for different movements."""
        try:
            self.injury_risk_factors = {
                "throwing": {
                    "shoulder_angle": {"high_risk": 90, "medium_risk": 80, "low_risk": 70},
                    "elbow_angle": {"high_risk": 30, "medium_risk": 45, "low_risk": 60},
                    "wrist_angle": {"high_risk": 30, "medium_risk": 45, "low_risk": 60}
                },
                "jumping": {
                    "knee_angle": {"high_risk": 30, "medium_risk": 45, "low_risk": 60},
                    "ankle_angle": {"high_risk": 30, "medium_risk": 45, "low_risk": 60},
                    "hip_angle": {"high_risk": 30, "medium_risk": 45, "low_risk": 60}
                }
            }
        except Exception as e:
            self.logger.error(f"Error loading injury risk factors: {str(e)}")
            raise

    async def load_custom_metrics(self):
        """Load custom metrics for different movements."""
        try:
            self.custom_metrics = {
                "throwing": {
                    "release_angle": {"optimal": 45, "range": (35, 55)},
                    "follow_through": {"optimal": 0.8, "range": (0.6, 1.0)},
                    "body_alignment": {"optimal": 0.9, "range": (0.7, 1.0)}
                },
                "jumping": {
                    "takeoff_angle": {"optimal": 45, "range": (40, 50)},
                    "landing_technique": {"optimal": 0.9, "range": (0.7, 1.0)},
                    "air_time": {"optimal": 0.5, "range": (0.4, 0.6)}
                }
            }
        except Exception as e:
            self.logger.error(f"Error loading custom metrics: {str(e)}")
            raise

    async def load_environmental_factors(self):
        """Load environmental factors that affect movement."""
        try:
            self.environmental_factors = {
                "temperature": {
                    "optimal": 20,  # Celsius
                    "range": (15, 25),
                    "impact": {
                        "cold": "Decreased flexibility, increased injury risk",
                        "hot": "Increased fatigue, dehydration risk"
                    }
                },
                "humidity": {
                    "optimal": 50,  # Percentage
                    "range": (40, 60),
                    "impact": {
                        "low": "Increased dehydration risk",
                        "high": "Increased fatigue, heat stress"
                    }
                },
                "altitude": {
                    "optimal": 0,  # Meters above sea level
                    "range": (0, 2000),
                    "impact": {
                        "high": "Decreased oxygen availability, increased fatigue"
                    }
                },
                "surface": {
                    "types": {
                        "hard": "Increased impact forces",
                        "soft": "Decreased stability",
                        "uneven": "Increased injury risk"
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Error loading environmental factors: {str(e)}")
            raise

    async def load_equipment_usage(self):
        """Load equipment usage guidelines."""
        try:
            self.equipment_usage = {
                "weights": {
                    "selection": {
                        "beginner": "Light weights, focus on form",
                        "intermediate": "Moderate weights, progressive overload",
                        "advanced": "Heavy weights, complex movements"
                    },
                    "safety": {
                        "spotters": "Required for heavy lifts",
                        "collars": "Required for all lifts",
                        "belts": "Optional for heavy lifts"
                    }
                },
                "machines": {
                    "selection": {
                        "beginner": "Fixed path machines",
                        "intermediate": "Cable machines",
                        "advanced": "Free weights and complex machines"
                    },
                    "safety": {
                        "settings": "Must be properly adjusted",
                        "maintenance": "Regular checks required",
                        "cleaning": "After each use"
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Error loading equipment usage: {str(e)}")
            raise

    @track_metrics
    async def analyze(self, processed_video: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method for processed video data."""
        try:
            start_time = datetime.now()
            
            # Extract movement patterns
            patterns = await self.extract_movement_patterns(processed_video)
            
            # Analyze patterns
            analysis = await self.analyze_movement_patterns(patterns)
            
            # Calculate metrics
            metrics = await self.calculate_movement_metrics(analysis)
            
            # Assess injury risk
            injury_risk = await self.assess_injury_risk(analysis, metrics)
            
            # Compare with benchmarks
            benchmark_comparison = await self.compare_with_benchmarks(analysis, metrics)
            
            # Generate feedback
            feedback = await self.generate_comprehensive_feedback(analysis, metrics)
            
            # Generate recommendations
            recommendations = await self.generate_recommendations(analysis, metrics)
            
            # Track progress
            progress = await self.track_progress(analysis, metrics)
            
            # Record analysis time
            end_time = datetime.now()
            analysis_time = (end_time - start_time).total_seconds()
            self.analysis_times.append(analysis_time)
            self.total_analyses += 1
            
            return {
                "analysis": analysis,
                "metrics": metrics,
                "injury_risk": injury_risk,
                "benchmark_comparison": benchmark_comparison,
                "feedback": feedback,
                "recommendations": recommendations,
                "progress": progress,
                "analysis_time": analysis_time
            }
            
        except Exception as e:
            self.logger.error(f"Error in movement analysis: {str(e)}")
            raise

    async def extract_movement_patterns(self, processed_video: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract movement patterns from processed video data."""
        try:
            return await self.movement_models.extract_patterns(processed_video)
        except Exception as e:
            self.logger.error(f"Error extracting movement patterns: {str(e)}")
            raise

    async def analyze_movement_patterns(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze extracted movement patterns."""
        try:
            # Use batch processing if enabled
            if self.optimization_config["batch_processing"]:
                return await self.analyze_patterns_batch(patterns)
            
            # Process patterns individually
            results = []
            for pattern in patterns:
                result = await self.analyze_single_pattern(pattern)
                results.append(result)
            
            return {
                "patterns": results,
                "count": len(results),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing movement patterns: {str(e)}")
            raise

    async def analyze_patterns_batch(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple movement patterns in a batch for better performance."""
        try:
            batch_hash = hash(str(patterns))
            
            # Check batch cache
            if batch_hash in self.batch_cache:
                self.cache_stats["hits"] += 1
                return self.batch_cache[batch_hash]
            
            self.cache_stats["misses"] += 1
            
            # Process patterns in parallel if enabled
            if self.optimization_config["parallel_processing"]:
                tasks = [
                    self.analyze_single_pattern(pattern)
                    for pattern in patterns
                ]
                results = await asyncio.gather(*tasks)
            else:
                results = [
                    await self.analyze_single_pattern(pattern)
                    for pattern in patterns
                ]
            
            # Update batch cache
            await self.manage_batch_cache()
            self.batch_cache[batch_hash] = results
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing pattern batch: {str(e)}")
            raise

    async def analyze_single_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single movement pattern with caching."""
        try:
            pattern_hash = hash(str(pattern))
            
            # Check analysis cache
            if pattern_hash in self.analysis_cache:
                self.cache_stats["hits"] += 1
                return self.analysis_cache[pattern_hash]
            
            self.cache_stats["misses"] += 1
            
            # Perform comprehensive analysis
            analysis = {
                "biomechanics": await self.analyze_biomechanics(pattern),
                "energy": await self.analyze_energy_efficiency(pattern),
                "symmetry": await self.analyze_symmetry(pattern),
                "skill": await self.assess_skill_level(pattern),
                "technique": await self.analyze_technique_variations(pattern),
                "consistency": await self.assess_movement_consistency(pattern),
                "fatigue": await self.analyze_fatigue(pattern),
                "environmental": await self.analyze_environmental_factors(pattern),
                "equipment": await self.analyze_equipment_usage(pattern)
            }
            
            # Update analysis cache
            await self.manage_analysis_cache()
            self.analysis_cache[pattern_hash] = analysis
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing single pattern: {str(e)}")
            raise

    # Real-time analysis methods
    async def analyze_posture_realtime(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze posture in real-time."""
        try:
            return await self.movement_models.analyze_posture(pattern)
        except Exception as e:
            self.logger.error(f"Error analyzing posture: {str(e)}")
            raise

    async def analyze_form_realtime(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze form in real-time."""
        try:
            return await self.movement_models.analyze_form(pattern)
        except Exception as e:
            self.logger.error(f"Error analyzing form: {str(e)}")
            raise

    async def analyze_alignment_realtime(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze alignment in real-time."""
        try:
            return await self.movement_models.analyze_alignment(pattern)
        except Exception as e:
            self.logger.error(f"Error analyzing alignment: {str(e)}")
            raise

    async def analyze_joint_stress_realtime(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze joint stress in real-time."""
        try:
            return await self.movement_models.analyze_joint_stress(pattern)
        except Exception as e:
            self.logger.error(f"Error analyzing joint stress: {str(e)}")
            raise

    async def analyze_balance_realtime(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze balance in real-time."""
        try:
            return await self.movement_models.analyze_balance(pattern)
        except Exception as e:
            self.logger.error(f"Error analyzing balance: {str(e)}")
            raise

    # Cache management methods
    async def manage_analysis_cache(self):
        """Manage analysis cache size and memory usage."""
        try:
            current_size = len(self.analysis_cache)
            if current_size > self.optimization_config["max_cache_size"]:
                # Remove oldest entries
                items = sorted(
                    self.analysis_cache.items(),
                    key=lambda x: x[1].get("timestamp", "")
                )
                items_to_remove = items[:current_size - self.optimization_config["max_cache_size"]]
                
                for key, _ in items_to_remove:
                    del self.analysis_cache[key]
                    self.cache_stats["evictions"] += 1
                    
            # Remove expired entries
            current_time = datetime.now().timestamp()
            expired_keys = [
                k for k, v in self.analysis_cache.items()
                if (current_time - datetime.fromisoformat(v.get("timestamp", "")).timestamp()) > self.optimization_config["cache_ttl"]
            ]
            
            for key in expired_keys:
                del self.analysis_cache[key]
                self.cache_stats["evictions"] += 1
                
        except Exception as e:
            self.logger.error(f"Error managing analysis cache: {str(e)}")
            raise

    async def manage_batch_cache(self):
        """Manage batch cache size and memory usage."""
        try:
            current_size = len(self.batch_cache)
            if current_size > self.optimization_config["max_batch_size"]:
                # Remove oldest entries
                items = sorted(self.batch_cache.items(), key=lambda x: x[0])
                items_to_remove = items[:current_size - self.optimization_config["max_batch_size"]]
                
                for key, _ in items_to_remove:
                    del self.batch_cache[key]
                    self.cache_stats["evictions"] += 1
                    
        except Exception as e:
            self.logger.error(f"Error managing batch cache: {str(e)}")
            raise

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        try:
            total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
            hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0
            
            return {
                "hits": self.cache_stats["hits"],
                "misses": self.cache_stats["misses"],
                "evictions": self.cache_stats["evictions"],
                "hit_rate": hit_rate,
                "analysis_cache_size": len(self.analysis_cache),
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
            
            analysis_cache_size = sum(sys.getsizeof(v) for v in self.analysis_cache.values())
            batch_cache_size = sum(sys.getsizeof(v) for v in self.batch_cache.values())
            
            return analysis_cache_size + batch_cache_size
            
        except Exception as e:
            self.logger.error(f"Error estimating memory usage: {str(e)}")
            return 0

    # Performance optimization methods
    def optimize_memory_usage(self) -> None:
        """Optimize memory usage based on current conditions."""
        try:
            # Clear caches if memory usage is too high
            if self._estimate_memory_usage() > self.optimization_config["memory_limit"]:
                self.clear_caches()
            
            # Adjust batch size
            self.optimization_config["batch_size"] = max(
                16,
                self.optimization_config["batch_size"] // 2
            )
            
            # Increase compression level if needed
            self.optimization_config["compression_level"] = min(
                3,
                self.optimization_config["compression_level"] + 1
            )
            
            self.logger.info("Memory usage optimization applied")
        except Exception as e:
            self.logger.error(f"Error optimizing memory usage: {str(e)}")

    def get_performance_report(self) -> Dict:
        """Generate a comprehensive performance report."""
        try:
            return {
                "resource_usage": {
                    "cpu": np.mean([v for _, v in self.real_time_monitoring["resource_usage"]["cpu_usage"]]),
                    "memory": np.mean([v for _, v in self.real_time_monitoring["resource_usage"]["memory_usage"]]),
                    "gpu": np.mean([v for _, v in self.real_time_monitoring["resource_usage"]["gpu_usage"]])
                },
                "error_rates": self.real_time_monitoring["error_rates"],
                "cache_efficiency": self.get_cache_stats()["hit_rate"],
                "adaptive_learning": {
                    "pattern_recognition": self.adaptive_learning["pattern_recognition"],
                    "performance_trends": self.adaptive_learning["performance_trends"],
                    "error_recovery": self.adaptive_learning["error_recovery"]
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}")
            return {}

    def clear_caches(self):
        """Clear all caches."""
        try:
            self.analysis_cache.clear()
            self.batch_cache.clear()
            self.cache_stats = {
                "hits": 0,
                "misses": 0,
                "evictions": 0
            }
            self.logger.info("All caches cleared")
        except Exception as e:
            self.logger.error(f"Error clearing caches: {str(e)}")

    # Monitoring initialization methods
    def initialize_adaptive_learning(self) -> None:
        """Initialize adaptive learning components."""
        self.adaptive_learning = {
            "pattern_recognition": {
                "learned_patterns": {},
                "confidence_scores": {},
                "adaptation_rate": 0.1
            },
            "performance_trends": {
                "historical_data": [],
                "trend_analysis": {},
                "prediction_models": {}
            },
            "error_recovery": {
                "error_patterns": {},
                "recovery_strategies": {},
                "success_rates": {}
            }
        }

    def initialize_real_time_monitoring(self) -> None:
        """Initialize real-time monitoring components."""
        self.real_time_monitoring = {
            "active_sessions": 0,
            "resource_usage": {
                "cpu_usage": [],
                "memory_usage": [],
                "gpu_usage": []
            },
            "error_rates": {
                "analysis_errors": 0,
                "processing_errors": 0,
                "recovery_attempts": 0
            }
        } 