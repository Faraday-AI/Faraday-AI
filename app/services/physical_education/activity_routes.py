from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from .models.activity import Activity
from .models.class_ import Class
from .models.student import Student 