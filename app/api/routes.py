from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.core.auth import get_current_user
from app.services.base_service import BaseService
from app.services.pe_service import PEService
from app.services.admin_service import AdminService
from app.services.secretary_service import SecretaryService

# Create main router
router = APIRouter()

# Service instances
services: Dict[str, BaseService] = {
    "pe": PEService("pe"),
    "admin": AdminService("admin"),
    "secretary": SecretaryService("secretary")
}

@router.get("/health")
async def health_check():
    """Check health of all services."""
    status = {}
    for service_type, service in services.items():
        status[service_type] = await service.get_service_status()
    return status

@router.post("/{service_type}/process")
async def process_request(
    service_type: str,
    request_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Process requests for any service type."""
    if service_type not in services:
        raise HTTPException(status_code=404, detail=f"Service type {service_type} not found")
    
    service = services[service_type]
    return await service.handle_request(request_data)

@router.get("/{service_type}/status")
async def get_service_status(
    service_type: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get status of specific service."""
    if service_type not in services:
        raise HTTPException(status_code=404, detail=f"Service type {service_type} not found")
    
    service = services[service_type]
    return await service.get_service_status()

# Service-specific routes
@router.post("/pe/analyze-movement")
async def analyze_movement(
    request_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze physical movement."""
    return await services["pe"].handle_request({
        "action": "analyze_movement",
        "data": request_data
    })

@router.post("/admin/process-enrollment")
async def process_enrollment(
    request_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Process student enrollment."""
    return await services["admin"].handle_request({
        "action": "process_enrollment",
        "data": request_data
    })

@router.post("/secretary/schedule-meeting")
async def schedule_meeting(
    request_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Schedule a meeting."""
    return await services["secretary"].handle_request({
        "action": "schedule_meeting",
        "data": request_data
    }) 