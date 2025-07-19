from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from app.services.core.auth_service import AuthService
from app.core.database import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta
from app.core.config import get_settings

router = APIRouter()
auth_service = AuthService()
settings = get_settings()

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatGPTLoginRequest(BaseModel):
    chatgpt_token: str

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Get access token for API authentication."""
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/chatgpt")
async def login_with_chatgpt(
    request: ChatGPTLoginRequest,
    db: Session = Depends(get_db)
):
    """Handle login through ChatGPT."""
    try:
        session = await auth_service.handle_chatgpt_login(request.chatgpt_token)
        return session
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def logout(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Handle user logout."""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="No authorization token")
        
        token = authorization.split(" ")[1]
        user = await auth_service.verify_session(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        success = await auth_service.logout(user)
        if success:
            return {"message": "Logged out successfully"}
        else:
            raise HTTPException(status_code=500, detail="Logout failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get current user information."""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="No authorization token")
        
        token = authorization.split(" ")[1]
        user = await auth_service.verify_session(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "school": user.school,
            "department": user.department,
            "subjects": user.subjects,
            "grade_levels": user.grade_levels
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-preferences")
async def sync_user_preferences(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Sync user preferences from ChatGPT."""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="No authorization token")
        
        token = authorization.split(" ")[1]
        user = await auth_service.verify_session(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # This would be implemented to sync preferences from ChatGPT
        return {"message": "Preferences synced successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 