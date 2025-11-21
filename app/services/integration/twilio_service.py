from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging
from functools import lru_cache
import backoff
from typing import Dict, Any
import phonenumbers
import asyncio
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.settings = get_settings()
        
        # Validate Twilio configuration
        if (self.settings.TWILIO_ACCOUNT_SID == "development" or 
            self.settings.TWILIO_AUTH_TOKEN == "development" or
            not self.settings.TWILIO_ACCOUNT_SID or 
            not self.settings.TWILIO_AUTH_TOKEN):
            logger.warning("Twilio credentials not configured. SMS functionality will not work.")
        
        if (self.settings.TWILIO_FROM_NUMBER == "+1234567890" or 
            not self.settings.TWILIO_FROM_NUMBER):
            logger.warning("Twilio 'From' number not configured. Please set TWILIO_FROM_NUMBER environment variable.")
        
        self.client = Client(
            self.settings.TWILIO_ACCOUNT_SID,
            self.settings.TWILIO_AUTH_TOKEN
        )

    def validate_phone_number(self, phone_number: str) -> str:
        """Validate and format phone number to E.164 format."""
        try:
            if not phone_number.startswith('+'):
                phone_number = f'+{phone_number}'
            parsed = phonenumbers.parse(phone_number)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            raise ValueError(f"Invalid phone number: {str(e)}")

    @backoff.on_exception(
        backoff.expo,
        (TwilioRestException),
        max_tries=3,
        max_time=30
    )
    async def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """
        Send an SMS message using Twilio.
        
        Args:
            to_number: The recipient's phone number (E.164 format)
            message: The message content
            
        Returns:
            Dict containing status and message details or error information
        """
        try:
            # Validate phone number
            to_number = self.validate_phone_number(to_number)

            # Send message (Twilio client is synchronous, run in thread pool)
            loop = asyncio.get_event_loop()
            message = await loop.run_in_executor(
                None,
                lambda: self.client.messages.create(
                body=message,
                from_=self.settings.TWILIO_FROM_NUMBER,
                to=to_number
            )
            )

            # Twilio message.status can be: queued, sending, sent, failed, etc.
            # If status is queued/sending/sent, we consider it successful
            twilio_status = message.status
            is_success = twilio_status in ["queued", "sending", "sent", "delivered"]

            return {
                "status": "success" if is_success else "pending",
                "message_sid": message.sid,
                "to": message.to,
                "from": message.from_,
                "twilio_status": twilio_status,
                "message": f"Message {twilio_status}. Message SID: {message.sid}"
            }

        except TwilioRestException as e:
            logger.error(f"Twilio API error: {str(e)}")
            error_msg = str(e)
            
            # Provide more helpful error messages
            if "From" in error_msg or "from" in error_msg.lower():
                if self.settings.TWILIO_FROM_NUMBER == "+1234567890" or not self.settings.TWILIO_FROM_NUMBER:
                    error_msg = "Twilio 'From' number is not configured. Please set TWILIO_FROM_NUMBER environment variable to a valid Twilio phone number."
                else:
                    error_msg = f"Twilio 'From' number ({self.settings.TWILIO_FROM_NUMBER}) is not valid for this account. Please verify the number in your Twilio console."
            
            return {
                "status": "error",
                "error": error_msg,
                "code": e.code,
                "details": "Please check your Twilio configuration. The 'From' number must be a valid Twilio phone number associated with your account."
            }
        except ValueError as e:
            # Phone number validation error
            logger.error(f"Phone number validation error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "details": "Please provide a valid phone number in E.164 format (e.g., +1234567890)"
            }
        except Exception as e:
            logger.error(f"Unexpected error in send_sms: {str(e)}")
            logger.exception("Full traceback:")
            return {
                "status": "error",
                "error": f"An unexpected error occurred: {str(e)}"
            }

    @backoff.on_exception(
        backoff.expo,
        (TwilioRestException),
        max_tries=3,
        max_time=30
    )
    async def make_call(self, to_number: str, message: str, language: str = "es-ES") -> Dict[str, Any]:
        """
        Make a voice call using Twilio.
        
        Args:
            to_number: The recipient's phone number (E.164 format)
            message: The message to speak
            language: The language voice to use (default: es-ES for Spanish)
            
        Returns:
            Dict containing status and call details or error information
        """
        try:
            # Validate phone number
            to_number = self.validate_phone_number(to_number)

            # Create TwiML for the call
            twiml = f"""
            <Response>
                <Say language="{language}">{message}</Say>
            </Response>
            """

            # Make the call (Twilio client is synchronous, run in thread pool)
            loop = asyncio.get_event_loop()
            call = await loop.run_in_executor(
                None,
                lambda: self.client.calls.create(
                twiml=twiml,
                to=to_number,
                from_=self.settings.TWILIO_FROM_NUMBER
                )
            )

            return {
                "status": "success",
                "call_sid": call.sid,
                "to": call.to,
                "from": call.from_,
                "status": call.status
            }

        except TwilioRestException as e:
            logger.error(f"Twilio API error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "code": e.code
            }
        except Exception as e:
            logger.error(f"Unexpected error in make_call: {str(e)}")
            return {
                "status": "error",
                "error": "An unexpected error occurred"
            }

@lru_cache()
def get_twilio_service() -> TwilioService:
    """Get cached Twilio service instance."""
    return TwilioService() 