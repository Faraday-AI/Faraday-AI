from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class VisualizationRequest(BaseModel):
    student_id: str = Field(..., description="ID of the student")
    start_date: datetime = Field(..., description="Start date for visualization data")
    end_date: datetime = Field(..., description="End date for visualization data")
    visualization_types: List[str] = Field(..., description="Types of visualizations to generate")
    interactive: bool = Field(True, description="Whether to generate interactive visualizations")
    drill_down: bool = Field(False, description="Whether to include drill-down capabilities")

class VisualizationResponse(BaseModel):
    visualization_id: str = Field(..., description="Unique identifier for the visualization")
    student_id: str = Field(..., description="ID of the student")
    type: str = Field(..., description="Type of visualization")
    data: Dict[str, Any] = Field(..., description="Visualization data")
    created_at: datetime = Field(..., description="When the visualization was created")
    interactive: bool = Field(..., description="Whether the visualization is interactive")
    drill_down: bool = Field(..., description="Whether the visualization has drill-down capabilities")

class ExportRequest(BaseModel):
    student_id: str = Field(..., description="ID of the student")
    start_date: datetime = Field(..., description="Start date for export data")
    end_date: datetime = Field(..., description="End date for export data")
    visualization_type: str = Field(..., description="Type of visualization to export")
    format: str = Field(..., description="Export format (e.g., png, pdf, svg)")

class ExportResponse(BaseModel):
    export_id: str = Field(..., description="Unique identifier for the export")
    student_id: str = Field(..., description="ID of the student")
    format: str = Field(..., description="Export format")
    file_path: str = Field(..., description="Path to the exported file")
    created_at: datetime = Field(..., description="When the export was created")
    size: int = Field(..., description="Size of the exported file in bytes") 