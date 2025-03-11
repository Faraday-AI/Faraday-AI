from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
import logging
from app.services.msgraph_service import get_msgraph_service

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Microsoft Graph API Test"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 