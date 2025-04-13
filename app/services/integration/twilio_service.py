from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging
from functools import lru_cache
import backoff
from typing import Dict, Any
import phonenumbers
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.settings = get_settings()
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

            # Send message
            message = await self.client.messages.create(
                body=message,
                from_=self.settings.TWILIO_FROM_NUMBER,
                to=to_number
            )

            return {
                "status": "success",
                "message_sid": message.sid,
                "to": message.to,
                "from": message.from_,
                "status": message.status
            }

        except TwilioRestException as e:
            logger.error(f"Twilio API error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "code": e.code
            }
        except Exception as e:
            logger.error(f"Unexpected error in send_sms: {str(e)}")
            return {
                "status": "error",
                "error": "An unexpected error occurred"
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

            # Make the call
            call = await self.client.calls.create(
                twiml=twiml,
                to=to_number,
                from_=self.settings.TWILIO_FROM_NUMBER
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