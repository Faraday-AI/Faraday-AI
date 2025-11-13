"""
Integration Models

This module contains models for external service integrations.
"""

from app.models.integration.microsoft_token import MicrosoftOAuthToken, BetaMicrosoftOAuthToken

__all__ = [
    "MicrosoftOAuthToken",
    "BetaMicrosoftOAuthToken",
]

