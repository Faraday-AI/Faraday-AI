from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from datetime import datetime
from ..models.collaboration import (
    CollaborationRequest,
    CollaborationResponse,
    GroupRequest,
    GroupResponse
)
from ..middleware.auth import oauth2_scheme, get_current_active_user
from app.services.physical_education.services.collaboration_manager import CollaborationManager

router = APIRouter()
collaboration_manager = CollaborationManager()

@router.post(
    "/collaboration/sessions",
    response_model=CollaborationSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create collaboration session",
    description="Creates a new collaboration session for activities",
    response_description="The created collaboration session"
)
async def create_collaboration_session(
    request: CollaborationSessionRequest,
    token: str = Depends(oauth2_scheme)
):
    """Create a new collaboration session."""
    try:
        result = await collaboration_manager.start_collaborative_session(
            session_id=request.session_id,
            participants=request.participants,
            activity_ids=request.activity_ids,
            settings=request.settings
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the collaboration session: {str(e)}"
        )

@router.post(
    "/collaboration/sessions/{session_id}/chat",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add chat message",
    description="Adds a chat message to a collaboration session",
    response_description="The created chat message"
)
async def add_chat_message(
    session_id: str,
    user_id: str,
    message: str,
    token: str = Depends(oauth2_scheme)
):
    """Add a chat message to a collaboration session."""
    try:
        result = await collaboration_manager.add_chat_message(
            session_id=session_id,
            user_id=user_id,
            message=message
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while adding the chat message: {str(e)}"
        )

@router.get(
    "/collaboration/sessions/{session_id}/chat",
    response_model=List[ChatMessageResponse],
    summary="Get chat messages",
    description="Retrieves chat messages for a collaboration session",
    response_description="List of chat messages"
)
async def get_chat_messages(
    session_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Get chat messages for a collaboration session."""
    try:
        result = await collaboration_manager.get_chat_messages(
            session_id=session_id
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving chat messages: {str(e)}"
        ) 