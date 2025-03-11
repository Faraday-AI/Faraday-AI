from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
import logging
from typing import Optional
import tempfile
import os

from app.core.config import get_settings
from app.services.openai_service import get_openai_service
from app.services.msgraph_service import get_msgraph_service
from app.services.twilio_service import get_twilio_service
from app.services.translation_service import get_translation_service
from app.models.api import (
    TextRequest, DocumentRequest, TokenResponse,
    UserInfoResponse, TextResponse, SMSRequest, SMSResponse,
    TranslationRequest, TranslationResponse,
    TranslatedMessageRequest, TranslatedMessageResponse,
    MessageType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title=get_settings().APP_NAME)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Microsoft Graph API Integration"}

@app.post("/test")
async def test():
    """Health check endpoint."""
    return {"status": "success", "message": "Service is running"}

@app.get("/login")
async def login(msgraph_service = Depends(get_msgraph_service)):
    """Initiate Microsoft Graph authentication."""
    try:
        auth_url = msgraph_service.get_auth_url()
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/callback")
async def callback(
    code: str,
    msgraph_service = Depends(get_msgraph_service)
) -> TokenResponse:
    """Handle Microsoft Graph authentication callback."""
    result = await msgraph_service.get_token(code)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return TokenResponse(**result)

@app.get("/me")
async def get_user_info(
    request: Request,
    msgraph_service = Depends(get_msgraph_service)
) -> UserInfoResponse:
    """Get user information from Microsoft Graph."""
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    
    result = await msgraph_service.get_user_info(token.split()[1])
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return UserInfoResponse(**result)

@app.post("/generate-text")
async def generate_text(
    request: TextRequest,
    openai_service = Depends(get_openai_service)
) -> TextResponse:
    """Generate text using OpenAI."""
    result = await openai_service.generate_text(
        request.prompt,
        request.structured_output
    )
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    return TextResponse(**result)

@app.post("/generate-document")
async def generate_document(request: DocumentRequest) -> FileResponse:
    """Generate a document in the specified format."""
    try:
        # Create a temporary file with the generated content
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{request.output_format}") as temp_file:
            if request.output_format == "docx":
                from docx import Document
                doc = Document()
                doc.add_heading(request.title, 0)
                doc.add_paragraph(request.content)
                doc.save(temp_file.name)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported format: {request.output_format}")

        return FileResponse(
            temp_file.name,
            media_type="application/octet-stream",
            filename=f"{request.title}.{request.output_format}"
        )
    except Exception as e:
        logger.error(f"Error generating document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary file
        if 'temp_file' in locals():
            os.unlink(temp_file.name)

@app.post("/send-sms")
async def send_sms(
    request: SMSRequest,
    twilio_service = Depends(get_twilio_service)
) -> SMSResponse:
    """Send an SMS message using Twilio."""
    result = await twilio_service.send_sms(
        request.to_number,
        request.message
    )
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    return SMSResponse(**result)

@app.post("/translate")
async def translate_text(
    request: TranslationRequest,
    translation_service = Depends(get_translation_service)
) -> TranslationResponse:
    """Translate text using Google Cloud Translation API."""
    result = await translation_service.translate_text(
        request.text,
        request.target_language,
        request.source_language
    )
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])
    return TranslationResponse(**result)

@app.post("/send-translated-message")
async def send_translated_message(
    request: TranslatedMessageRequest,
    translation_service = Depends(get_translation_service),
    twilio_service = Depends(get_twilio_service)
) -> TranslatedMessageResponse:
    """Translate and send a message via SMS or voice call."""
    try:
        # First, translate the message
        translation_result = await translation_service.translate_text(
            request.message,
            request.target_language,
            request.source_language
        )
        
        if translation_result["status"] == "error":
            raise HTTPException(status_code=500, detail=translation_result["error"])
        
        translated_text = translation_result["translated_text"]
        
        # Then, send the translated message
        if request.message_type == MessageType.SMS:
            delivery_result = await twilio_service.send_sms(
                request.to_number,
                translated_text
            )
            if delivery_result["status"] == "error":
                raise HTTPException(status_code=500, detail=delivery_result["error"])
            
            return TranslatedMessageResponse(
                status="success",
                original_text=request.message,
                translated_text=translated_text,
                message_type="sms",
                delivery_status=delivery_result["status"],
                message_sid=delivery_result.get("message_sid")
            )
        else:  # Voice call
            delivery_result = await twilio_service.make_call(
                request.to_number,
                translated_text,
                f"{request.target_language}-{request.target_language.upper()}"
            )
            if delivery_result["status"] == "error":
                raise HTTPException(status_code=500, detail=delivery_result["error"])
            
            return TranslatedMessageResponse(
                status="success",
                original_text=request.message,
                translated_text=translated_text,
                message_type="voice",
                delivery_status=delivery_result["status"],
                call_sid=delivery_result.get("call_sid")
            )
            
    except Exception as e:
        logger.error(f"Error in send_translated_message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 