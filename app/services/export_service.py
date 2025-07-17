"""
Export service for Faraday AI.

This module provides functionality for exporting data in various formats.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import csv
import io
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.core.core_models import ExportFormat, FileType

class ExportService:
    """Service for handling data exports."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def export_data(
        self,
        data: List[Dict[str, Any]],
        format: ExportFormat,
        file_type: FileType,
        filename: Optional[str] = None
    ) -> bytes:
        """Export data in the specified format and file type.
        
        Args:
            data: The data to export
            format: The export format (JSON, CSV, etc.)
            file_type: The file type to export as
            filename: Optional filename for the export
            
        Returns:
            bytes: The exported data
            
        Raises:
            HTTPException: If export fails
        """
        try:
            if format == ExportFormat.JSON:
                return self._export_json(data)
            elif format == ExportFormat.CSV:
                return self._export_csv(data)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported export format: {format}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Export failed: {str(e)}"
            )
    
    def _export_json(self, data: List[Dict[str, Any]]) -> bytes:
        """Export data as JSON."""
        return json.dumps(data, default=str).encode('utf-8')
    
    def _export_csv(self, data: List[Dict[str, Any]]) -> bytes:
        """Export data as CSV."""
        if not data:
            return b""
            
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue().encode('utf-8') 