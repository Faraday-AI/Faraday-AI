"""
Competition Participant Models

This module exports participant-related models.
"""

from app.models.competition.participants.participant import CompetitionParticipant
from app.models.competition.participants.event_participant import EventParticipant

__all__ = [
    'CompetitionParticipant',
    'EventParticipant'
] 