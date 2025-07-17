from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.activity import Activity
from app.models.physical_education.class_.models import PhysicalEducationClass
from app.models.student import Student 