from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from typing import Optional
import tempfile
import os
from pathlib import Path

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
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Faraday AI",
    root_path="",  # Remove root_path to handle paths from the actual root
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define base directory - use absolute paths
BASE_DIR = Path(__file__).resolve().parent.absolute()
STATIC_DIR = BASE_DIR / "static"
IMAGES_DIR = STATIC_DIR / "images"

# Ensure directories exist and log their creation
os.makedirs(str(STATIC_DIR), exist_ok=True)
os.makedirs(str(IMAGES_DIR), exist_ok=True)

logger.info(f"Starting server with BASE_DIR: {BASE_DIR}")
logger.info(f"STATIC_DIR exists: {STATIC_DIR.exists()}")
logger.info(f"IMAGES_DIR exists: {IMAGES_DIR.exists()}")
logger.info(f"Current working directory: {os.getcwd()}")

# Mount static files with explicit check
if not STATIC_DIR.exists():
    logger.error(f"Static directory does not exist: {STATIC_DIR}")
    os.makedirs(str(STATIC_DIR), exist_ok=True)
    logger.info(f"Created static directory: {STATIC_DIR}")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

# Root route
@app.get("/")
async def read_root():
    try:
        logger.info(f"Handling root request")
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info(f"BASE_DIR: {BASE_DIR}")
        logger.info(f"STATIC_DIR: {STATIC_DIR}")
        logger.info(f"IMAGES_DIR: {IMAGES_DIR}")
        
        # Check if the image exists
        image_path = IMAGES_DIR / "coming-soon.png"
        logger.info(f"Looking for image at: {image_path}")
        logger.info(f"Image exists: {image_path.exists()}")
        
        if not image_path.exists():
            logger.warning("Image not found, returning text-only response")
            return HTMLResponse(content="<h1>Coming Soon - Faraday AI</h1>")
        
        # Log image details
        image_size = os.path.getsize(str(image_path))
        logger.info(f"Image size: {image_size} bytes")
        logger.info(f"Image permissions: {oct(os.stat(str(image_path)).st_mode)[-3:]}")
        
        html_content = f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Faraday AI - Coming Soon</title>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body {{ 
                            margin: 0; 
                            display: flex; 
                            justify-content: center; 
                            align-items: center; 
                            min-height: 100vh; 
                            background: #1a1a1a; 
                            font-family: Arial, sans-serif;
                            color: white;
                        }}
                        .container {{ 
                            text-align: center;
                            padding: 20px;
                        }}
                        img {{ 
                            max-width: 100%; 
                            height: auto; 
                            display: block;
                            margin: 0 auto;
                        }}
                        h1 {{
                            margin-top: 20px;
                            font-size: 2em;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <img 
                            src="/static/images/coming-soon.png" 
                            alt="Coming Soon"
                            onerror="this.onerror=null; this.src=''; this.alt='Image failed to load'; console.error('Image failed to load');"
                        >
                        <h1>Faraday AI - Coming Soon</h1>
                    </div>
                    <script>
                        document.addEventListener('DOMContentLoaded', function() {{
                            const img = document.querySelector('img');
                            img.addEventListener('load', function() {{
                                console.log('Image loaded successfully');
                            }});
                            img.addEventListener('error', function() {{
                                console.error('Image failed to load');
                            }});
                        }});
                    </script>
                </body>
            </html>
        """
        logger.info("Returning HTML response with image")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error serving index: {str(e)}")
        return HTMLResponse(content="<h1>Coming Soon - Faraday AI</h1>")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "cwd": os.getcwd(),
        "base_dir": str(BASE_DIR),
        "static_dir": str(STATIC_DIR),
        "images_dir": str(IMAGES_DIR),
        "image_exists": (IMAGES_DIR / "coming-soon.png").exists(),
        "files_in_static": os.listdir(str(STATIC_DIR)) if STATIC_DIR.exists() else [],
        "files_in_images": os.listdir(str(IMAGES_DIR)) if IMAGES_DIR.exists() else []
    }

@app.get("/login")
async def login(msgraph_service = Depends(get_msgraph_service)):
    """Initiate Microsoft Graph authentication."""
    try:
        auth_url = msgraph_service.get_auth_url()
        logger.debug(f"Generated auth URL: {auth_url}")
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
    try:
        result = await msgraph_service.get_token(code)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        return TokenResponse(**result)
    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

@app.get("/static/images/{image_name}")
async def get_image(image_name: str):
    """Serve images directly."""
    try:
        image_path = IMAGES_DIR / image_name
        logger.info(f"Attempting to serve image: {image_path}")
        
        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            raise HTTPException(status_code=404, detail="Image not found")
            
        logger.info(f"Image exists, size: {os.path.getsize(str(image_path))} bytes")
        return FileResponse(
            str(image_path),
            media_type="image/png",
            filename=image_name
        )
    except Exception as e:
        logger.error(f"Error serving image {image_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}") 