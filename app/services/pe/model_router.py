"""
Model Router
Routes requests to specialized service or fallback router.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from openai import OpenAI
import logging

from app.services.pe.specialized_services.service_registry import ServiceRegistry
from app.services.pe.base_widget_service import BaseWidgetService

logger = logging.getLogger(__name__)


class ModelRouter:
    """Routes requests to specialized service or fallback router."""

    def __init__(self, db: Session = None, openai_client: OpenAI = None):
        """
        Initialize ModelRouter.
        
        Args:
            db: Database session (required for ServiceRegistry)
            openai_client: OpenAI client (required for ServiceRegistry and fallback)
        """
        if not db or not openai_client:
            logger.warning("⚠️ ModelRouter initialized without db/openai_client - registry will be None")
            self.registry = None
        else:
            self.registry = ServiceRegistry(db, openai_client)
        
        self.db = db
        self.openai_client = openai_client
        self.fallback_model = "gpt-4o-mini"
        self.fallback_prompt = "prompts/jasper_router.txt"

    def route(self, intent: str, user_request: str, context: dict = None) -> dict:
        """
        Route request to specialized service or fallback.
        
        Args:
            intent: The classified intent string
            user_request: User's request message
            context: Optional context dictionary
            
        Returns:
            Dictionary with response data
        """
        if context is None:
            context = {}
        
        # Try to get specialized service from registry
        if self.registry:
            service = self.registry.get_service(intent)
            if service:
                logger.info(f"✅ ModelRouter: Routing to specialized service for intent '{intent}'")
                return service.process(user_request, context)
        
        # Fallback to lightweight router
        logger.info(f"⚠️ ModelRouter: No specialized service for intent '{intent}', using fallback")
        return self._fallback(user_request, context)

    def _fallback(self, user_request: str, context: dict) -> dict:
        """
        Fallback to lightweight router prompt.
        
        Args:
            user_request: User's request message
            context: Context dictionary
            
        Returns:
            Dictionary with response data
        """
        # Use BaseWidgetService for fallback (auto-creates client from env if needed)
        service = BaseWidgetService(db=self.db, openai_client=self.openai_client)
        service.prompt_file = self.fallback_prompt
        service.model = self.fallback_model
        
        return service.process(user_request, context)

