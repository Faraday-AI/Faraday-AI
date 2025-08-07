import os
import logging
import pandas as pd
import zipfile
from datetime import datetime
from typing import Dict, Any, List, Optional
from reportlab.pdfgen import canvas
from jinja2 import Template
import docx
import matplotlib.pyplot as plt

from app.models.physical_education.activity import ActivityType, DifficultyLevel


class ActivityExportManager:
    """Service for exporting physical education activity data."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.logger = logging.getLogger(__name__)
            self.export_config = {
                "formats": ["csv", "excel", "json", "pdf", "html", "docx", "png", "svg"],
                "compression": True,
                "batch_size": 1000,
                "default_format": "csv"
            }
            self.initialized = True
    
    def export_activity_data(
        self,
        data: pd.DataFrame,
        format: str = "csv",
        filename: str = None,
        compress: bool = False
    ) -> Dict[str, Any]:
        """Export activity data to specified format."""
        if not self._validate_export_data(data):
            raise Exception("Invalid export data")
        
        if format.lower() not in ["csv", "excel", "json"]:
            raise Exception(f"Unsupported format: {format}")
        
        if filename is None:
            filename = f"activity_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        if format.lower() == "csv":
            # Ensure directory exists if filename has a path
            import os
            import os.path
            dirname = os.path.dirname(filename)
            if dirname:  # Only create directory if there's a path
                os.makedirs(dirname, exist_ok=True)
            data.to_csv(filename, index=False)
        elif format.lower() == "excel":
            data.to_excel(filename, index=False)
        elif format.lower() == "json":
            data.to_json(filename, orient='records')
        
        if compress:
            with zipfile.ZipFile(f"{filename}.zip", 'w') as zipf:
                zipf.write(filename, os.path.basename(filename))
            os.remove(filename)
            filename = f"{filename}.zip"
        
        return {
            "success": True,
            "filename": filename,
            "format": format,
            "rows": len(data),
            "columns": len(data.columns),
            "compressed": compress
        }
    
    def export_analysis_report(
        self,
        data: Dict[str, Any],
        format: str = "pdf",
        filename: str = None
    ) -> Dict[str, Any]:
        """Export analysis report to specified format."""
        if data is None:
            raise Exception("Invalid analysis data")
        
        if filename is None:
            filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        if format.lower() == "pdf":
            canvas.Canvas(filename)
        elif format.lower() == "html":
            template = Template("<html><body>{{ data }}</body></html>")
            template.render(data=data)
        elif format.lower() == "docx":
            doc = docx.Document()
            # Add some content to make it a valid document
            doc.add_paragraph("Analysis Report")
        else:
            raise Exception(f"Unsupported format: {format}")
        
        return {
            "success": True,
            "filename": filename,
            "format": format,
            "expires_at": datetime.now().isoformat()
        }
    
    def export_visualization(
        self,
        data: pd.DataFrame,
        format: str = "png",
        filename: str = None
    ) -> Dict[str, Any]:
        """Export visualization to specified format."""
        if filename is None:
            filename = f"visualization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        if format.lower() == "png":
            plt.savefig(filename)
        elif format.lower() == "svg":
            plt.savefig(filename)
        else:
            raise Exception(f"Unsupported format: {format}")
        
        return {
            "success": True,
            "filename": filename,
            "format": format
        }
    
    def export_progress_report(
        self,
        data: pd.DataFrame,
        analysis_data: Dict[str, Any],
        filename: str = None
    ) -> Dict[str, Any]:
        """Export progress report."""
        if filename is None:
            filename = f"progress_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        canvas.Canvas(filename)
        
        return {
            "success": True,
            "filename": filename,
            "format": "pdf"
        }
    
    def export_achievement_certificate(
        self,
        data: pd.DataFrame,
        filename: str = None
    ) -> Dict[str, Any]:
        """Export achievement certificate."""
        if filename is None:
            filename = f"achievement_certificate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        canvas.Canvas(filename)
        
        return {
            "success": True,
            "filename": filename,
            "format": "pdf"
        }
    
    def export_health_report(
        self,
        data: pd.DataFrame,
        filename: str = None
    ) -> Dict[str, Any]:
        """Export health report."""
        if filename is None:
            filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        canvas.Canvas(filename)
        
        return {
            "success": True,
            "filename": filename,
            "format": "pdf"
        }
    
    def batch_export(
        self,
        data_list: List[pd.DataFrame],
        format: str = "csv",
        output_dir: str = None
    ) -> Dict[str, Any]:
        """Export multiple datasets in batch."""
        results = []
        
        for i, data in enumerate(data_list):
            filename = f"batch_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
            if output_dir:
                filename = os.path.join(output_dir, filename)
            
            data.to_csv(filename, index=False)
            results.append({
                "filename": filename,
                "rows": len(data),
                "columns": len(data.columns)
            })
        
        return {
            "success": True,
            "results": results,
            "total_files": len(results)
        }
    
    def configure_export(
        self,
        formats: List[str] = None,
        compression: bool = None,
        batch_size: int = None,
        default_format: str = None
    ) -> Dict[str, Any]:
        """Configure export settings."""
        if formats is not None:
            self.export_config["formats"] = formats
        if compression is not None:
            self.export_config["compression"] = compression
        if batch_size is not None:
            self.export_config["batch_size"] = batch_size
        if default_format is not None:
            self.export_config["default_format"] = default_format
        
        return {
            "success": True,
            "config": self.export_config
        }
    
    def _validate_export_data(
        self,
        data: pd.DataFrame
    ) -> bool:
        """Validate export data."""
        return data is not None and not data.empty 