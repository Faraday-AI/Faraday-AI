import os
import sys
from pathlib import Path

# Add the current directory to the Python path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

# Set environment variables
os.environ["PYTHONPATH"] = str(current_dir)
os.environ["APP_ENVIRONMENT"] = os.getenv("APP_ENVIRONMENT", "production")
os.environ["DEBUG"] = os.getenv("DEBUG", "false")
os.environ["LOG_LEVEL"] = os.getenv("LOG_LEVEL", "info")

# Import and run the FastAPI app
from app.main import app 