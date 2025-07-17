"""
Base Educational Models

This module exports all base educational models.
"""

from app.models.educational.base.grade import Grade
from app.models.educational.base.assignment import Assignment
from app.models.educational.base.rubric import Rubric
from app.models.educational.base.message import Message
from app.models.educational.base.message_board import MessageBoard, MessageBoardPost

__all__ = [
    'Grade',
    'Assignment',
    'Rubric',
    'Message',
    'MessageBoard',
    'MessageBoardPost'
] 