from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.dashboard.dependencies import get_db, get_current_user
from app.models.educational import Grade, Assignment, Rubric, Message, MessageBoard, MessageBoardPost
from app.schemas.educational import (
    GradeCreate,
    GradeUpdate,
    GradeResponse,
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentResponse,
    RubricCreate,
    RubricResponse,
    MessageCreate,
    MessageResponse,
    MessageBoardCreate,
    MessageBoardResponse,
    MessageBoardPostCreate,
    MessageBoardPostResponse
)

router = APIRouter()

# Grade endpoints
@router.post("/grades", response_model=GradeResponse)
async def create_grade(
    grade: GradeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new grade entry"""
    if not current_user.has_permission("edit_grades"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_grade = Grade(
        student_id=grade.student_id,
        assignment_id=grade.assignment_id,
        grade=grade.grade,
        feedback=grade.feedback,
        grader_id=current_user.id,
        status="graded"
    )
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade

@router.get("/grades/{student_id}", response_model=List[GradeResponse])
async def get_student_grades(
    student_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all grades for a student"""
    if not current_user.has_permission("view_grades"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    grades = db.query(Grade).filter(Grade.student_id == student_id).all()
    return grades

# Assignment endpoints
@router.post("/assignments", response_model=AssignmentResponse)
async def create_assignment(
    assignment: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new assignment"""
    if not current_user.has_permission("create_assignments"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_assignment = Assignment(
        title=assignment.title,
        description=assignment.description,
        due_date=assignment.due_date,
        created_by=current_user.id,
        course_id=assignment.course_id,
        rubric_id=assignment.rubric_id,
        status="draft"
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@router.get("/assignments", response_model=List[AssignmentResponse])
async def get_assignments(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all assignments, optionally filtered by course"""
    query = db.query(Assignment)
    if course_id:
        query = query.filter(Assignment.course_id == course_id)
    assignments = query.all()
    return assignments

# Message endpoints
@router.post("/messages", response_model=MessageResponse)
async def send_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send a new message"""
    if not current_user.has_permission("send_messages"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_message = Message(
        sender_id=current_user.id,
        recipient_id=message.recipient_id,
        subject=message.subject,
        content=message.content,
        status="sent"
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.get("/messages", response_model=List[MessageResponse])
async def get_messages(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all messages for the current user"""
    messages = db.query(Message).filter(
        (Message.sender_id == current_user.id) | 
        (Message.recipient_id == current_user.id)
    ).all()
    return messages

# Message board endpoints
@router.post("/message-boards", response_model=MessageBoardResponse)
async def create_message_board(
    board: MessageBoardCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new message board"""
    if not current_user.has_permission("create_boards"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_board = MessageBoard(
        title=board.title,
        description=board.description,
        created_by=current_user.id,
        course_id=board.course_id,
        is_private=board.is_private
    )
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board

@router.get("/message-boards", response_model=List[MessageBoardResponse])
async def get_message_boards(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all message boards, optionally filtered by course"""
    query = db.query(MessageBoard)
    if course_id:
        query = query.filter(MessageBoard.course_id == course_id)
    boards = query.all()
    return boards

@router.post("/message-boards/{board_id}/posts", response_model=MessageBoardPostResponse)
async def create_board_post(
    board_id: int,
    post: MessageBoardPostCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new post on a message board"""
    if not current_user.has_permission("post_to_boards"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_post = MessageBoardPost(
        board_id=board_id,
        author_id=current_user.id,
        content=post.content,
        status="active"
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post 