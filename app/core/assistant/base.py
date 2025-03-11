from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel
from datetime import datetime
import openai
from app.core.config import get_settings
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)
settings = get_settings()

class AssistantCapability(BaseModel):
    """Base model for assistant capabilities."""
    name: str
    description: str
    enabled: bool = True
    requires_permissions: List[str] = []
    config: Dict[str, Any] = {}

class AssistantMessage(BaseModel):
    """Model for assistant messages."""
    content: str
    role: str
    timestamp: datetime = datetime.now()
    metadata: Dict[str, Any] = {}

class AssistantContext(BaseModel):
    """Model for assistant context."""
    user_id: str
    role: str
    preferences: Dict[str, Any] = {}
    session_data: Dict[str, Any] = {}
    permissions: List[str] = []

class BaseAssistant(ABC):
    """Base class for all AI assistants in the platform."""
    
    def __init__(self, context: AssistantContext):
        self.context = context
        self.openai_client = openai.Client(api_key=settings.OPENAI_API_KEY)
        self.conversation_history: List[AssistantMessage] = []
        self.capabilities: Dict[str, AssistantCapability] = {}
        self._initialize_capabilities()

    @abstractmethod
    def _initialize_capabilities(self):
        """Initialize assistant-specific capabilities."""
        pass

    async def process_message(
        self,
        message: str,
        metadata: Dict[str, Any] = None
    ) -> AssistantMessage:
        """Process incoming message and generate response."""
        try:
            # Add user message to history
            self.conversation_history.append(
                AssistantMessage(
                    content=message,
                    role="user",
                    metadata=metadata or {}
                )
            )

            # Generate response using context and history
            response = await self._generate_response(message)

            # Add assistant response to history
            assistant_message = AssistantMessage(
                content=response,
                role="assistant",
                metadata={"generated_by": self.__class__.__name__}
            )
            self.conversation_history.append(assistant_message)

            return assistant_message

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

    async def _generate_response(self, message: str) -> str:
        """Generate response using OpenAI API."""
        try:
            # Prepare conversation context
            system_prompt = self._build_system_prompt()
            
            messages = [
                {"role": "system", "content": system_prompt},
                *[
                    {"role": msg.role, "content": msg.content}
                    for msg in self.conversation_history[-5:]  # Last 5 messages for context
                ],
                {"role": "user", "content": message}
            ]

            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    def _build_system_prompt(self) -> str:
        """Build system prompt based on context and capabilities."""
        return f"""You are an AI assistant for {self.context.role} in the school community.
Your capabilities include: {', '.join(self.capabilities.keys())}
User preferences: {self.context.preferences}

Guidelines:
1. Provide accurate and helpful information
2. Maintain appropriate tone for {self.context.role}
3. Respect user permissions and privacy
4. Follow educational best practices
5. Encourage critical thinking and learning

Current session context:
{self.context.session_data}
"""

    async def add_capability(self, capability: AssistantCapability):
        """Add new capability to assistant."""
        if not all(perm in self.context.permissions for perm in capability.requires_permissions):
            raise PermissionError(f"Missing required permissions for capability: {capability.name}")
        
        self.capabilities[capability.name] = capability

    async def remove_capability(self, capability_name: str):
        """Remove capability from assistant."""
        if capability_name in self.capabilities:
            del self.capabilities[capability_name]

    async def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation."""
        return {
            "message_count": len(self.conversation_history),
            "duration": (datetime.now() - self.conversation_history[0].timestamp).seconds if self.conversation_history else 0,
            "topics": await self._analyze_conversation_topics(),
            "sentiment": await self._analyze_conversation_sentiment()
        }

    async def _analyze_conversation_topics(self) -> List[str]:
        """Analyze conversation topics using AI."""
        if not self.conversation_history:
            return []

        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in self.conversation_history[-10:]  # Analyze last 10 messages
        ])

        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "Analyze the conversation and identify the main topics discussed. Return as a comma-separated list."
                },
                {
                    "role": "user",
                    "content": conversation_text
                }
            ],
            temperature=0.3
        )

        return [topic.strip() for topic in response.choices[0].message.content.split(",")]

    async def _analyze_conversation_sentiment(self) -> Dict[str, float]:
        """Analyze conversation sentiment using AI."""
        if not self.conversation_history:
            return {"positive": 0.0, "neutral": 1.0, "negative": 0.0}

        recent_messages = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in self.conversation_history[-5:]  # Analyze last 5 messages
        ])

        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "Analyze the conversation sentiment and return scores as JSON: {positive: float, neutral: float, negative: float}"
                },
                {
                    "role": "user",
                    "content": recent_messages
                }
            ],
            temperature=0.3
        )

        try:
            import json
            return json.loads(response.choices[0].message.content)
        except:
            return {"positive": 0.0, "neutral": 1.0, "negative": 0.0}

    def save_state(self) -> Dict[str, Any]:
        """Save assistant state for persistence."""
        return {
            "context": self.context.dict(),
            "conversation_history": [msg.dict() for msg in self.conversation_history],
            "capabilities": {name: cap.dict() for name, cap in self.capabilities.items()}
        }

    @classmethod
    def load_state(cls, state: Dict[str, Any]) -> 'BaseAssistant':
        """Load assistant state from persistence."""
        context = AssistantContext(**state["context"])
        assistant = cls(context)
        
        assistant.conversation_history = [
            AssistantMessage(**msg)
            for msg in state["conversation_history"]
        ]
        
        assistant.capabilities = {
            name: AssistantCapability(**cap)
            for name, cap in state["capabilities"].items()
        }
        
        return assistant 