"""
Base AI Service - Phase 3

This module provides a base class for AI services with common functionality
for analytics, predictions, and intelligence features.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import logging
import json
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BaseAIService:
    """Base class for AI services with common functionality."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def validate_input_data(self, data: Dict[str, Any]) -> bool:
        """Validate input data for AI processing."""
        try:
            if not isinstance(data, dict):
                return False
            
            # Check for required fields
            required_fields = self._get_required_fields()
            for field in required_fields:
                if field not in data:
                    self.logger.warning(f"Missing required field: {field}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating input data: {e}")
            return False
    
    def _get_required_fields(self) -> List[str]:
        """Get list of required fields for validation."""
        return []
    
    async def preprocess_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess data for AI analysis."""
        try:
            processed_data = data.copy()
            
            # Clean and normalize data
            processed_data = self._clean_data(processed_data)
            
            # Add metadata
            processed_data["processed_at"] = datetime.utcnow().isoformat()
            processed_data["processing_version"] = "v1.0.0"
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error preprocessing data: {e}")
            return data
    
    def _clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize data."""
        cleaned_data = {}
        
        for key, value in data.items():
            if value is not None:
                # Convert numeric strings to numbers
                if isinstance(value, str):
                    try:
                        if '.' in value:
                            cleaned_data[key] = float(value)
                        else:
                            cleaned_data[key] = int(value)
                    except ValueError:
                        cleaned_data[key] = value
                else:
                    cleaned_data[key] = value
        
        return cleaned_data
    
    async def postprocess_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess AI results."""
        try:
            processed_results = results.copy()
            
            # Add metadata
            processed_results["processed_at"] = datetime.utcnow().isoformat()
            processed_results["processing_version"] = "v1.0.0"
            
            # Validate results
            if self._validate_results(processed_results):
                processed_results["validation_status"] = "valid"
            else:
                processed_results["validation_status"] = "invalid"
                self.logger.warning("Results validation failed")
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Error postprocessing results: {e}")
            return results
    
    def _validate_results(self, results: Dict[str, Any]) -> bool:
        """Validate AI results."""
        try:
            # Basic validation - check for required result fields
            required_result_fields = self._get_required_result_fields()
            for field in required_result_fields:
                if field not in results:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating results: {e}")
            return False
    
    def _get_required_result_fields(self) -> List[str]:
        """Get list of required result fields for validation."""
        return []
    
    async def handle_errors(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle errors gracefully and return fallback data."""
        self.logger.error(f"Error in {context}: {error}")
        
        return {
            "error": str(error),
            "error_context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "fallback_data": True
        }
    
    def calculate_confidence_score(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score for AI predictions."""
        try:
            # Simple confidence calculation based on data quality
            confidence = 0.5  # Base confidence
            
            # Increase confidence based on data completeness
            if data.get("completeness_score", 0) > 0.8:
                confidence += 0.2
            
            # Increase confidence based on data consistency
            if data.get("consistency_score", 0) > 0.8:
                confidence += 0.2
            
            # Increase confidence based on historical accuracy
            if data.get("historical_accuracy", 0) > 0.8:
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence score: {e}")
            return 0.5
    
    async def log_ai_activity(self, activity_type: str, data: Dict[str, Any], 
                            user_id: Optional[int] = None) -> None:
        """Log AI activity for monitoring and debugging."""
        try:
            log_entry = {
                "activity_type": activity_type,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data_summary": self._summarize_data(data),
                "service": self.__class__.__name__
            }
            
            self.logger.info(f"AI Activity: {json.dumps(log_entry, indent=2)}")
            
        except Exception as e:
            self.logger.error(f"Error logging AI activity: {e}")
    
    def _summarize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of data for logging."""
        try:
            summary = {
                "data_type": type(data).__name__,
                "keys": list(data.keys()) if isinstance(data, dict) else [],
                "size": len(str(data))
            }
            
            # Add specific summaries for different data types
            if isinstance(data, dict):
                summary["has_user_id"] = "user_id" in data
                summary["has_timestamp"] = "timestamp" in data
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error summarizing data: {e}")
            return {"error": str(e)} 