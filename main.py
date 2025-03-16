from app.main import app

if __name__ == "__main__":
    import uvicorn
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("uvicorn")
    logger.setLevel(logging.DEBUG)
    
    # Run with detailed logging
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",
        access_log=True
    )

