from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Grade schemas
class GradeBase(BaseModel):
    student_id: int
    assignment_id: int
    grade: float
    feedback: Optional[str] = None

class GradeCreate(GradeBase):
    pass

class GradeUpdate(BaseModel):
    grade: Optional[float] = None
    feedback: Optional[str] = None
    status: Optional[str] = None

class GradeResponse(GradeBase):
    id: int
    submitted_at: datetime
    graded_at: Optional[datetime] = None
    grader_id: int
    status: str

    class Config:
        from_attributes = True

# Assignment schemas
class AssignmentBase(BaseModel):
    title: str
    description: str
    due_date: datetime
    course_id: int
    rubric_id: Optional[int] = None

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None

class AssignmentResponse(AssignmentBase):
    id: int
    created_by: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Rubric schemas
class RubricBase(BaseModel):
    name: str
    criteria: dict
    total_points: float

class RubricCreate(RubricBase):
    pass

class RubricResponse(RubricBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Message schemas
class MessageBase(BaseModel):
    recipient_id: int
    subject: str
    content: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    sent_at: datetime
    read_at: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True

# Message Board schemas
class MessageBoardBase(BaseModel):
    title: str
    description: str
    course_id: int
    is_private: bool = False

class MessageBoardCreate(MessageBoardBase):
    pass

class MessageBoardResponse(MessageBoardBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Message Board Post schemas
class MessageBoardPostBase(BaseModel):
    content: str

class MessageBoardPostCreate(MessageBoardPostBase):
    pass

class MessageBoardPostResponse(MessageBoardPostBase):
    id: int
    board_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    status: str

    class Config:
        from_attributes = True 