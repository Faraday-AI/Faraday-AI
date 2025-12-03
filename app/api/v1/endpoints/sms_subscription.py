"""
SMS Subscription API endpoints for Twilio SMS opt-in management.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field, validator
import logging

from app.dashboard.dependencies import get_db
from app.models.communication.models import SMSSubscription
from app.services.integration.twilio_service import get_twilio_service
import phonenumbers

logger = logging.getLogger(__name__)

router = APIRouter()


class SMSOptInRequest(BaseModel):
    """Request model for SMS opt-in."""
    phone_number: str = Field(..., description="Phone number in any format (will be normalized to E.164)")
    email: Optional[str] = Field(None, description="Optional email address")
    message_types: Optional[list[str]] = Field(
        None,
        description="List of message types user wants to receive. Defaults to all types."
    )
    source: Optional[str] = Field("homepage", description="Source of the opt-in (e.g., 'homepage', 'dashboard')")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate and normalize phone number."""
        try:
            # Try to parse the phone number
            if not v.startswith('+'):
                # If it doesn't start with +, try adding country code
                if v.startswith('1') and len(v) == 11:
                    v = '+' + v
                elif len(v) == 10:
                    # Assume US number
                    v = '+1' + v
                else:
                    v = '+' + v
            
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            
            # Return in E.164 format
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            raise ValueError(f"Invalid phone number format: {str(e)}")


class SMSOptInResponse(BaseModel):
    """Response model for SMS opt-in."""
    success: bool
    message: str
    phone_number: str
    subscription_id: Optional[int] = None
    confirmation_sent: bool = False


class SMSOptOutRequest(BaseModel):
    """Request model for SMS opt-out."""
    phone_number: str = Field(..., description="Phone number in E.164 format")


@router.post("/opt-in", response_model=SMSOptInResponse)
async def sms_opt_in(
    request: SMSOptInRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Opt-in to receive SMS messages from Faraday AI.
    
    This endpoint:
    - Validates the phone number
    - Stores the subscription with consent information
    - Sends a confirmation SMS message
    - Returns subscription details
    """
    try:
        # Get client IP and user agent for consent tracking
        client_ip = None
        user_agent = None
        if http_request:
            client_ip = http_request.client.host if http_request.client else None
            user_agent = http_request.headers.get("user-agent")
        
        # Check if subscription already exists
        existing_subscription = db.query(SMSSubscription).filter(
            SMSSubscription.phone_number == request.phone_number
        ).first()
        
        if existing_subscription:
            # If already opted out, reactivate
            if existing_subscription.opted_out:
                existing_subscription.opted_out = False
                existing_subscription.opted_out_date = None
                existing_subscription.is_active = True
                existing_subscription.consent_given = True
                existing_subscription.consent_date = datetime.utcnow()
                existing_subscription.consent_ip_address = client_ip
                existing_subscription.consent_user_agent = user_agent
                if request.email:
                    existing_subscription.email = request.email
                if request.message_types:
                    existing_subscription.message_types = request.message_types
                existing_subscription.source = request.source or "homepage"
                db.commit()
                
                # Send confirmation message
                twilio_service = get_twilio_service()
                confirmation_message = (
                    "You've been re-subscribed to Faraday AI SMS updates for educational purposes. "
                    "You'll receive messages from your child's teacher/school including account alerts, "
                    "educational updates, and important notifications. "
                    "Reply STOP to opt out anytime. Reply HELP for assistance."
                )
                sms_result = await twilio_service.send_sms(request.phone_number, confirmation_message)
                
                return SMSOptInResponse(
                    success=True,
                    message="Successfully re-subscribed to SMS updates. A confirmation message has been sent.",
                    phone_number=request.phone_number,
                    subscription_id=existing_subscription.id,
                    confirmation_sent=sms_result.get("status") == "success"
                )
            else:
                # Already subscribed and active
                return SMSOptInResponse(
                    success=True,
                    message="You are already subscribed to SMS updates.",
                    phone_number=request.phone_number,
                    subscription_id=existing_subscription.id,
                    confirmation_sent=False
                )
        
        # Create new subscription
        subscription = SMSSubscription(
            phone_number=request.phone_number,
            phone_number_formatted=request.phone_number,  # Already in E.164 format
            email=request.email,
            consent_given=True,
            consent_date=datetime.utcnow(),
            consent_ip_address=client_ip,
            consent_user_agent=user_agent,
            is_active=True,
            opted_out=False,
            message_types=request.message_types or [
                "account_alerts",
                "educational_updates",
                "product_announcements",
                "service_notifications"
            ],
            source=request.source or "homepage",
            subscription_metadata={"opt_in_method": "web_form"}
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        # Send confirmation SMS
        twilio_service = get_twilio_service()
        confirmation_message = (
            "Welcome to Faraday AI SMS updates for educational purposes! "
            "You'll receive messages from your child's teacher/school including account alerts, "
            "educational resources, and important notifications. "
            "Message and data rates may apply. Reply STOP to opt out anytime. Reply HELP for assistance."
        )
        sms_result = await twilio_service.send_sms(request.phone_number, confirmation_message)
        
        logger.info(f"SMS opt-in successful for {request.phone_number}. Subscription ID: {subscription.id}")
        
        return SMSOptInResponse(
            success=True,
            message="Successfully subscribed to SMS updates. A confirmation message has been sent.",
            phone_number=request.phone_number,
            subscription_id=subscription.id,
            confirmation_sent=sms_result.get("status") == "success"
        )
        
    except ValueError as e:
        logger.error(f"Validation error in SMS opt-in: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError as e:
        logger.error(f"Database integrity error in SMS opt-in: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A subscription with this phone number already exists."
        )
    except Exception as e:
        logger.error(f"Unexpected error in SMS opt-in: {str(e)}")
        logger.exception("Full traceback:")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your subscription. Please try again later."
        )


@router.post("/opt-out", response_model=Dict[str, Any])
async def sms_opt_out(
    request: SMSOptOutRequest,
    db: Session = Depends(get_db)
):
    """
    Opt-out from receiving SMS messages.
    
    This endpoint:
    - Finds the subscription by phone number
    - Marks it as opted out
    - Sends a confirmation message
    """
    try:
        # Normalize phone number
        try:
            if not request.phone_number.startswith('+'):
                if request.phone_number.startswith('1') and len(request.phone_number) == 11:
                    phone_normalized = '+' + request.phone_number
                elif len(request.phone_number) == 10:
                    phone_normalized = '+1' + request.phone_number
                else:
                    phone_normalized = '+' + request.phone_number
            else:
                phone_normalized = request.phone_number
            
            parsed = phonenumbers.parse(phone_normalized, None)
            phone_normalized = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            raise ValueError(f"Invalid phone number format: {str(e)}")
        
        # Find subscription
        subscription = db.query(SMSSubscription).filter(
            SMSSubscription.phone_number == phone_normalized
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=404,
                detail="No active subscription found for this phone number."
            )
        
        if subscription.opted_out:
            return {
                "success": True,
                "message": "You are already opted out of SMS updates.",
                "phone_number": phone_normalized
            }
        
        # Mark as opted out
        subscription.opted_out = True
        subscription.opted_out_date = datetime.utcnow()
        subscription.is_active = False
        db.commit()
        
        # Send confirmation message
        twilio_service = get_twilio_service()
        confirmation_message = (
            "You have been unsubscribed from Faraday AI SMS updates. "
            "You will no longer receive messages from us. "
            "To opt back in, visit our website or text START to this number."
        )
        sms_result = await twilio_service.send_sms(phone_normalized, confirmation_message)
        
        logger.info(f"SMS opt-out successful for {phone_normalized}. Subscription ID: {subscription.id}")
        
        return {
            "success": True,
            "message": "Successfully opted out of SMS updates. A confirmation message has been sent.",
            "phone_number": phone_normalized,
            "confirmation_sent": sms_result.get("status") == "success"
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error in SMS opt-out: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in SMS opt-out: {str(e)}")
        logger.exception("Full traceback:")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your opt-out. Please try again later."
        )


@router.get("/status/{phone_number}", response_model=Dict[str, Any])
async def get_sms_subscription_status(
    phone_number: str,
    db: Session = Depends(get_db)
):
    """
    Get the subscription status for a phone number.
    """
    try:
        # Normalize phone number
        try:
            if not phone_number.startswith('+'):
                if phone_number.startswith('1') and len(phone_number) == 11:
                    phone_normalized = '+' + phone_number
                elif len(phone_number) == 10:
                    phone_normalized = '+1' + phone_number
                else:
                    phone_normalized = '+' + phone_number
            else:
                phone_normalized = phone_number
            
            parsed = phonenumbers.parse(phone_normalized, None)
            phone_normalized = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            raise ValueError(f"Invalid phone number format: {str(e)}")
        
        subscription = db.query(SMSSubscription).filter(
            SMSSubscription.phone_number == phone_normalized
        ).first()
        
        if not subscription:
            return {
                "subscribed": False,
                "phone_number": phone_normalized,
                "message": "No subscription found for this phone number."
            }
        
        return {
            "subscribed": subscription.is_active and not subscription.opted_out,
            "phone_number": phone_normalized,
            "subscription_id": subscription.id,
            "consent_date": subscription.consent_date.isoformat() if subscription.consent_date else None,
            "opted_out": subscription.opted_out,
            "opted_out_date": subscription.opted_out_date.isoformat() if subscription.opted_out_date else None,
            "message_types": subscription.message_types,
            "total_messages_sent": subscription.total_messages_sent
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting SMS subscription status: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while checking subscription status.")

