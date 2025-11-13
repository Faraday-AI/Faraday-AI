"""
Microsoft Integration Health Check Endpoints

Provides health check and status monitoring for Microsoft Graph integration.
"""

import logging
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.integration.msgraph_service import get_msgraph_service
from app.models.integration.microsoft_token import MicrosoftOAuthToken, BetaMicrosoftOAuthToken

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health/microsoft",
    tags=["microsoft-health"],
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Microsoft service unavailable"}
    }
)


@router.get(
    "/",
    summary="Microsoft Integration Health Check",
    description="Check the health status of Microsoft Graph integration"
)
async def microsoft_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Check Microsoft Graph service health and configuration."""
    try:
        msgraph_service = get_msgraph_service()
        
        # Check service configuration
        is_configured = msgraph_service.client is not None
        has_credentials = all([
            msgraph_service.settings.CLIENT_ID,
            msgraph_service.settings.CLIENT_SECRET,
            msgraph_service.settings.TENANT_ID,
            msgraph_service.settings.REDIRECT_URI
        ])
        
        # Count active tokens
        active_tokens_main = db.query(MicrosoftOAuthToken).filter(
            MicrosoftOAuthToken.is_active == True
        ).count()
        
        active_tokens_beta = db.query(BetaMicrosoftOAuthToken).filter(
            BetaMicrosoftOAuthToken.is_active == True
        ).count()
        
        # Check token encryption service
        from app.services.integration.token_encryption import get_token_encryption_service
        encryption_service = get_token_encryption_service()
        encryption_available = encryption_service._fernet is not None
        
        health_status = "healthy" if (is_configured and has_credentials) else "degraded"
        
        return {
            "status": health_status,
            "service": "microsoft_graph",
            "configured": is_configured,
            "credentials_available": has_credentials,
            "encryption_available": encryption_available,
            "active_tokens": {
                "main_system": active_tokens_main,
                "beta_system": active_tokens_beta,
                "total": active_tokens_main + active_tokens_beta
            },
            "last_check": datetime.utcnow().isoformat(),
            "details": {
                "client_id_set": bool(msgraph_service.settings.CLIENT_ID),
                "client_secret_set": bool(msgraph_service.settings.CLIENT_SECRET),
                "tenant_id_set": bool(msgraph_service.settings.TENANT_ID),
                "redirect_uri_set": bool(msgraph_service.settings.REDIRECT_URI),
            }
        }
    except Exception as e:
        logger.error(f"Error checking Microsoft health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Microsoft health check failed: {str(e)}"
        )


@router.get(
    "/tokens",
    summary="Microsoft Token Statistics",
    description="Get statistics about stored Microsoft OAuth tokens"
)
async def microsoft_token_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get statistics about Microsoft OAuth tokens."""
    try:
        from datetime import datetime, timedelta
        
        now = datetime.utcnow()
        
        # Main system stats
        main_total = db.query(MicrosoftOAuthToken).count()
        main_active = db.query(MicrosoftOAuthToken).filter(
            MicrosoftOAuthToken.is_active == True
        ).count()
        main_expired = db.query(MicrosoftOAuthToken).filter(
            MicrosoftOAuthToken.expires_at < now
        ).count()
        main_expiring_soon = db.query(MicrosoftOAuthToken).filter(
            MicrosoftOAuthToken.expires_at <= now + timedelta(minutes=5),
            MicrosoftOAuthToken.expires_at > now
        ).count()
        
        # Beta system stats
        beta_total = db.query(BetaMicrosoftOAuthToken).count()
        beta_active = db.query(BetaMicrosoftOAuthToken).filter(
            BetaMicrosoftOAuthToken.is_active == True
        ).count()
        beta_expired = db.query(BetaMicrosoftOAuthToken).filter(
            BetaMicrosoftOAuthToken.expires_at < now
        ).count()
        beta_expiring_soon = db.query(BetaMicrosoftOAuthToken).filter(
            BetaMicrosoftOAuthToken.expires_at <= now + timedelta(minutes=5),
            BetaMicrosoftOAuthToken.expires_at > now
        ).count()
        
        return {
            "main_system": {
                "total": main_total,
                "active": main_active,
                "expired": main_expired,
                "expiring_soon": main_expiring_soon,
                "inactive": main_total - main_active
            },
            "beta_system": {
                "total": beta_total,
                "active": beta_active,
                "expired": beta_expired,
                "expiring_soon": beta_expiring_soon,
                "inactive": beta_total - beta_active
            },
            "summary": {
                "total_tokens": main_total + beta_total,
                "total_active": main_active + beta_active,
                "total_expired": main_expired + beta_expired,
                "total_expiring_soon": main_expiring_soon + beta_expiring_soon
            },
            "last_updated": now.isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting token statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get token statistics: {str(e)}"
        )

