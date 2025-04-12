from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from datetime import datetime
import os
from app.api.v1.models.visualization import (
    VisualizationRequest,
    VisualizationResponse,
    ExportRequest,
    ExportResponse
)
from app.api.v1.middleware.auth import oauth2_scheme, get_current_active_user
from app.services.physical_education.services.activity_manager import ActivityManager
from app.services.physical_education.services.activity_visualization_manager import ActivityVisualizationManager
from app.services.physical_education.services.activity_export_manager import ActivityExportManager

router = APIRouter()
activity_manager = ActivityManager()
visualization_manager = ActivityVisualizationManager()
export_manager = ActivityExportManager()

@router.post(
    "/visualizations",
    response_model=List[VisualizationResponse],
    summary="Generate visualizations",
    description="Generates visualizations for a student's activities",
    response_description="List of generated visualizations"
)
async def generate_visualizations(
    request: VisualizationRequest,
    token: str = Depends(oauth2_scheme)
):
    """Generate visualizations for a student."""
    try:
        activities = await activity_manager.get_activities(
            student_id=request.student_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        skills = await activity_manager.get_skills(
            student_id=request.student_id
        )
        
        result = await visualization_manager.generate_visualizations(
            student_id=request.student_id,
            performance_data=activities,
            skill_data=skills,
            visualization_types=request.visualization_types,
            interactive=request.interactive,
            drill_down=request.drill_down
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating visualizations: {str(e)}"
        )

@router.post(
    "/export",
    response_model=ExportResponse,
    summary="Export visualization",
    description="Exports a visualization in the specified format",
    response_description="The exported file information"
)
async def export_visualization(
    request: ExportRequest,
    token: str = Depends(oauth2_scheme)
):
    """Export a visualization in the specified format."""
    try:
        activities = await activity_manager.get_activities(
            student_id=request.student_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        visualization = await visualization_manager.generate_visualizations(
            student_id=request.student_id,
            performance_data=activities,
            visualization_types=[request.visualization_type],
            interactive=False
        )[0]
        
        result = await export_manager.export_visualization(
            visualization=visualization,
            format=request.format,
            student_id=request.student_id
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while exporting the visualization: {str(e)}"
        ) 