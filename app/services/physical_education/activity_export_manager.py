"""Activity export manager for physical education."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.core.database import get_db

# Import models
from app.models.activity import (
    Activity,
    ActivityCategoryAssociation
)
from app.models.student import Student
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)
from app.models.cache import (
    CachePolicy,
    CacheEntry,
    CacheMetrics,
    CacheStatus
)
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    ActivityCategoryType,
    ExportFormat,
    FileType,
    CompressionType,
    DataFormat
)

class ActivityExportManager:
    """Service for exporting physical education activity data."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ActivityExportManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger("activity_export_manager")
        self.db = None
        
        # Export settings
        self.settings = {
            "default_format": "csv",
            "compression": {
                "enabled": True,
                "type": "gzip",
                "level": 6
            },
            "file_types": {
                "csv": {
                    "delimiter": ",",
                    "encoding": "utf-8",
                    "date_format": "%Y-%m-%d %H:%M:%S"
                },
                "excel": {
                    "engine": "openpyxl",
                    "sheet_name": "Activity Data",
                    "date_format": "YYYY-MM-DD HH:MM:SS"
                },
                "json": {
                    "indent": 2,
                    "date_format": "iso"
                }
            },
            "batch_size": 1000,
            "max_rows": 1000000
        }
        
        # Export components
        self.export_history = []
        self.export_templates = {}
        self.data_transformers = {}
        self.validation_rules = {}
        
        # Caching and optimization
        self.export_cache = {}
        self.template_cache = {}
    
    async def initialize(self):
        """Initialize the export manager."""
        try:
            self.db = next(get_db())
            
            # Load export templates
            await self.load_export_templates()
            
            # Initialize export components
            self.initialize_export_components()
            
            self.logger.info("Activity Export Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Activity Export Manager: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the export manager."""
        try:
            # Clear all data
            self.export_history.clear()
            self.export_templates.clear()
            self.data_transformers.clear()
            self.validation_rules.clear()
            self.export_cache.clear()
            self.template_cache.clear()
            
            # Reset service references
            self.db = None
            
            self.logger.info("Activity Export Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Activity Export Manager: {str(e)}")
            raise

    async def load_export_templates(self):
        """Load export templates for different data types."""
        try:
            self.export_templates = {
                "performance": {
                    "fields": [
                        "student_id",
                        "activity_id",
                        "score",
                        "date",
                        "notes"
                    ],
                    "transformers": {
                        "date": "to_datetime",
                        "score": "to_float",
                        "notes": "clean_text"
                    },
                    "validators": {
                        "score": "validate_score",
                        "date": "validate_date"
                    }
                },
                "activity": {
                    "fields": [
                        "id",
                        "name",
                        "description",
                        "type",
                        "difficulty",
                        "equipment_required"
                    ],
                    "transformers": {
                        "type": "to_enum",
                        "difficulty": "to_enum",
                        "equipment_required": "to_list"
                    },
                    "validators": {
                        "type": "validate_type",
                        "difficulty": "validate_difficulty"
                    }
                }
            }
            
            self.logger.info("Export templates loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading export templates: {str(e)}")
            raise

    def initialize_export_components(self):
        """Initialize export components."""
        try:
            # Initialize data transformers
            self.data_transformers = {
                "to_datetime": self._transform_to_datetime,
                "to_float": self._transform_to_float,
                "clean_text": self._clean_text,
                "to_enum": self._transform_to_enum,
                "to_list": self._transform_to_list
            }
            
            # Initialize validation rules
            self.validation_rules = {
                "validate_score": self._validate_score,
                "validate_date": self._validate_date,
                "validate_type": self._validate_type,
                "validate_difficulty": self._validate_difficulty
            }
            
            self.logger.info("Export components initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing export components: {str(e)}")
            raise

    async def export_performance_data(
        self,
        student_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "csv",
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Export student performance data."""
        try:
            # Get performance data
            data = await self._get_performance_data(
                student_id, start_date, end_date
            )
            
            # Apply template transformations
            transformed_data = self._apply_template_transformations(
                data, "performance"
            )
            
            # Validate data
            self._validate_data(transformed_data, "performance")
            
            # Export data
            export_result = await self._export_data(
                transformed_data,
                format,
                include_metadata
            )
            
            # Update export history
            self._update_export_history(
                student_id,
                "performance",
                format,
                export_result
            )
            
            return export_result
            
        except Exception as e:
            self.logger.error(f"Error exporting performance data: {str(e)}")
            raise

    async def export_activity_data(
        self,
        activity_type: Optional[str] = None,
        format: str = "csv",
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Export activity data."""
        try:
            # Get activity data
            data = await self._get_activity_data(activity_type)
            
            # Apply template transformations
            transformed_data = self._apply_template_transformations(
                data, "activity"
            )
            
            # Validate data
            self._validate_data(transformed_data, "activity")
            
            # Export data
            export_result = await self._export_data(
                transformed_data,
                format,
                include_metadata
            )
            
            # Update export history
            self._update_export_history(
                None,
                "activity",
                format,
                export_result
            )
            
            return export_result
            
        except Exception as e:
            self.logger.error(f"Error exporting activity data: {str(e)}")
            raise

    def _apply_template_transformations(
        self,
        data: pd.DataFrame,
        template_type: str
    ) -> pd.DataFrame:
        """Apply template transformations to data."""
        try:
            template = self.export_templates[template_type]
            transformed_data = data.copy()
            
            # Apply field transformations
            for field, transformer in template["transformers"].items():
                if field in transformed_data.columns:
                    transform_func = self.data_transformers[transformer]
                    transformed_data[field] = transformed_data[field].apply(transform_func)
            
            return transformed_data
            
        except Exception as e:
            self.logger.error(f"Error applying template transformations: {str(e)}")
            raise

    def _validate_data(self, data: pd.DataFrame, template_type: str) -> None:
        """Validate data against template rules."""
        try:
            template = self.export_templates[template_type]
            
            # Apply validation rules
            for field, validator in template["validators"].items():
                if field in data.columns:
                    validate_func = self.validation_rules[validator]
                    invalid_rows = ~data[field].apply(validate_func)
                    if invalid_rows.any():
                        raise ValueError(f"Invalid values in {field} column")
            
        except Exception as e:
            self.logger.error(f"Error validating data: {str(e)}")
            raise

    async def _export_data(
        self,
        data: pd.DataFrame,
        format: str,
        include_metadata: bool
    ) -> Dict[str, Any]:
        """Export data to specified format."""
        try:
            if format not in self.settings["file_types"]:
                raise ValueError(f"Unsupported format: {format}")
            
            # Get format settings
            format_settings = self.settings["file_types"][format]
            
            # Prepare export data
            export_data = data.copy()
            
            if include_metadata:
                metadata = self._generate_metadata(export_data)
                
            # Export based on format
            if format == "csv":
                result = self._export_to_csv(export_data, format_settings)
            elif format == "excel":
                result = self._export_to_excel(export_data, format_settings)
            elif format == "json":
                result = self._export_to_json(export_data, format_settings)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            if include_metadata:
                result["metadata"] = metadata
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {str(e)}")
            raise

    def _export_to_csv(
        self,
        data: pd.DataFrame,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export data to CSV format."""
        try:
            # Export to CSV
            csv_data = data.to_csv(
                index=False,
                sep=settings["delimiter"],
                encoding=settings["encoding"],
                date_format=settings["date_format"]
            )
            
            # Apply compression if enabled
            if self.settings["compression"]["enabled"]:
                csv_data = self._compress_data(csv_data)
            
            return {
                "format": "csv",
                "data": csv_data,
                "rows": len(data),
                "columns": len(data.columns),
                "compressed": self.settings["compression"]["enabled"]
            }
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
            raise

    def _export_to_excel(
        self,
        data: pd.DataFrame,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export data to Excel format."""
        try:
            # Export to Excel
            excel_data = data.to_excel(
                None,
                sheet_name=settings["sheet_name"],
                index=False,
                engine=settings["engine"]
            )
            
            # Apply compression if enabled
            if self.settings["compression"]["enabled"]:
                excel_data = self._compress_data(excel_data)
            
            return {
                "format": "excel",
                "data": excel_data,
                "rows": len(data),
                "columns": len(data.columns),
                "compressed": self.settings["compression"]["enabled"]
            }
            
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {str(e)}")
            raise

    def _export_to_json(
        self,
        data: pd.DataFrame,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export data to JSON format."""
        try:
            # Export to JSON
            json_data = data.to_json(
                orient="records",
                date_format=settings["date_format"],
                indent=settings["indent"]
            )
            
            # Apply compression if enabled
            if self.settings["compression"]["enabled"]:
                json_data = self._compress_data(json_data)
            
            return {
                "format": "json",
                "data": json_data,
                "rows": len(data),
                "columns": len(data.columns),
                "compressed": self.settings["compression"]["enabled"]
            }
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {str(e)}")
            raise

    def _compress_data(self, data: Any) -> bytes:
        """Compress data using configured compression settings."""
        try:
            import gzip
            import zlib
            
            if self.settings["compression"]["type"] == "gzip":
                return gzip.compress(
                    data.encode() if isinstance(data, str) else data,
                    compresslevel=self.settings["compression"]["level"]
                )
            elif self.settings["compression"]["type"] == "zlib":
                return zlib.compress(
                    data.encode() if isinstance(data, str) else data,
                    level=self.settings["compression"]["level"]
                )
            else:
                raise ValueError(f"Unsupported compression type: {self.settings['compression']['type']}")
            
        except Exception as e:
            self.logger.error(f"Error compressing data: {str(e)}")
            raise

    def _generate_metadata(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate metadata for exported data."""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "rows": len(data),
                "columns": len(data.columns),
                "column_types": data.dtypes.to_dict(),
                "missing_values": data.isnull().sum().to_dict(),
                "memory_usage": data.memory_usage(deep=True).sum()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating metadata: {str(e)}")
            raise

    def _update_export_history(
        self,
        student_id: Optional[str],
        export_type: str,
        format: str,
        result: Dict[str, Any]
    ) -> None:
        """Update export history."""
        try:
            self.export_history.append({
                "timestamp": datetime.now().isoformat(),
                "student_id": student_id,
                "type": export_type,
                "format": format,
                "rows": result["rows"],
                "columns": result["columns"],
                "compressed": result.get("compressed", False)
            })
            
        except Exception as e:
            self.logger.error(f"Error updating export history: {str(e)}")
            raise

    # Data transformation methods
    def _transform_to_datetime(self, value: Any) -> datetime:
        """Transform value to datetime."""
        try:
            return pd.to_datetime(value)
        except Exception as e:
            self.logger.error(f"Error transforming to datetime: {str(e)}")
            return None

    def _transform_to_float(self, value: Any) -> float:
        """Transform value to float."""
        try:
            return float(value)
        except Exception as e:
            self.logger.error(f"Error transforming to float: {str(e)}")
            return None

    def _clean_text(self, value: Any) -> str:
        """Clean text value."""
        try:
            if pd.isna(value):
                return ""
            return str(value).strip()
        except Exception as e:
            self.logger.error(f"Error cleaning text: {str(e)}")
            return ""

    def _transform_to_enum(self, value: Any) -> str:
        """Transform value to enum string."""
        try:
            if pd.isna(value):
                return None
            return str(value).upper()
        except Exception as e:
            self.logger.error(f"Error transforming to enum: {str(e)}")
            return None

    def _transform_to_list(self, value: Any) -> List[str]:
        """Transform value to list."""
        try:
            if pd.isna(value):
                return []
            if isinstance(value, str):
                return [item.strip() for item in value.split(",")]
            if isinstance(value, list):
                return value
            return [str(value)]
        except Exception as e:
            self.logger.error(f"Error transforming to list: {str(e)}")
            return []

    # Validation methods
    def _validate_score(self, value: Any) -> bool:
        """Validate score value."""
        try:
            if pd.isna(value):
                return False
            score = float(value)
            return 0 <= score <= 100
        except Exception:
            return False

    def _validate_date(self, value: Any) -> bool:
        """Validate date value."""
        try:
            if pd.isna(value):
                return False
            pd.to_datetime(value)
            return True
        except Exception:
            return False

    def _validate_type(self, value: Any) -> bool:
        """Validate type value."""
        try:
            if pd.isna(value):
                return False
            return str(value).upper() in [t.value for t in ActivityType]
        except Exception:
            return False

    def _validate_difficulty(self, value: Any) -> bool:
        """Validate difficulty value."""
        try:
            if pd.isna(value):
                return False
            return str(value).upper() in [d.value for d in DifficultyLevel]
        except Exception:
            return False 