from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class ConversationContextService:
    def __init__(self):
        self.contexts: Dict[str, Dict[str, Any]] = {}
        self.threads: Dict[str, List[Dict[str, Any]]] = {}
        self.context_ttl = timedelta(hours=24)

    async def create_context(
        self,
        context_id: str,
        initial_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new conversation context."""
        try:
            context = {
                "id": context_id,
                "created_at": datetime.utcnow(),
                "last_updated": datetime.utcnow(),
                "data": initial_context,
                "metadata": {},
                "active": True
            }
            self.contexts[context_id] = context
            self.threads[context_id] = []
            return {"status": "success", "context": context}
        except Exception as e:
            logger.error(f"Error creating context: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def update_context(
        self,
        context_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing conversation context."""
        try:
            if context_id not in self.contexts:
                return {
                    "status": "error",
                    "error": "Context not found"
                }

            context = self.contexts[context_id]
            context["data"].update(updates)
            context["last_updated"] = datetime.utcnow()
            return {"status": "success", "context": context}
        except Exception as e:
            logger.error(f"Error updating context: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def get_context(
        self,
        context_id: str
    ) -> Dict[str, Any]:
        """Get conversation context by ID."""
        try:
            if context_id not in self.contexts:
                return {
                    "status": "error",
                    "error": "Context not found"
                }

            context = self.contexts[context_id]
            if datetime.utcnow() - context["last_updated"] > self.context_ttl:
                context["active"] = False

            return {"status": "success", "context": context}
        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def add_message_to_thread(
        self,
        context_id: str,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a message to a conversation thread."""
        try:
            if context_id not in self.threads:
                return {
                    "status": "error",
                    "error": "Thread not found"
                }

            message_with_metadata = {
                **message,
                "timestamp": datetime.utcnow(),
                "message_id": f"{context_id}_{len(self.threads[context_id])}"
            }
            self.threads[context_id].append(message_with_metadata)

            # Update context last_updated
            if context_id in self.contexts:
                self.contexts[context_id]["last_updated"] = datetime.utcnow()

            return {"status": "success", "message": message_with_metadata}
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def get_thread_messages(
        self,
        context_id: str,
        limit: Optional[int] = None,
        before_timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get messages from a conversation thread."""
        try:
            if context_id not in self.threads:
                return {
                    "status": "error",
                    "error": "Thread not found"
                }

            messages = self.threads[context_id]
            
            if before_timestamp:
                messages = [
                    msg for msg in messages
                    if msg["timestamp"] < before_timestamp
                ]

            if limit:
                messages = messages[-limit:]

            return {"status": "success", "messages": messages}
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def analyze_context(
        self,
        context_id: str
    ) -> Dict[str, Any]:
        """Analyze conversation context for insights."""
        try:
            if context_id not in self.contexts or context_id not in self.threads:
                return {
                    "status": "error",
                    "error": "Context or thread not found"
                }

            context = self.contexts[context_id]
            messages = self.threads[context_id]

            # Calculate basic metrics
            total_messages = len(messages)
            user_messages = sum(1 for msg in messages if msg.get("role") == "user")
            assistant_messages = sum(1 for msg in messages if msg.get("role") == "assistant")
            avg_response_time = 0

            if len(messages) > 1:
                response_times = []
                for i in range(1, len(messages)):
                    if messages[i].get("role") == "assistant" and messages[i-1].get("role") == "user":
                        time_diff = messages[i]["timestamp"] - messages[i-1]["timestamp"]
                        response_times.append(time_diff.total_seconds())
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)

            # Extract common topics or themes (simple implementation)
            all_content = " ".join(msg.get("content", "") for msg in messages)
            words = all_content.lower().split()
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1

            top_topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]

            analysis = {
                "metrics": {
                    "total_messages": total_messages,
                    "user_messages": user_messages,
                    "assistant_messages": assistant_messages,
                    "avg_response_time": avg_response_time,
                    "conversation_duration": (
                        messages[-1]["timestamp"] - messages[0]["timestamp"]
                        if messages else timedelta(0)
                    ).total_seconds()
                },
                "topics": [{"word": word, "frequency": freq} for word, freq in top_topics],
                "context_age": (
                    datetime.utcnow() - context["created_at"]
                ).total_seconds(),
                "is_active": context["active"]
            }

            return {"status": "success", "analysis": analysis}
        except Exception as e:
            logger.error(f"Error analyzing context: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def cleanup_old_contexts(self) -> Dict[str, Any]:
        """Clean up expired conversation contexts."""
        try:
            current_time = datetime.utcnow()
            expired_contexts = []

            for context_id, context in list(self.contexts.items()):
                if current_time - context["last_updated"] > self.context_ttl:
                    expired_contexts.append(context_id)
                    del self.contexts[context_id]
                    if context_id in self.threads:
                        del self.threads[context_id]

            return {
                "status": "success",
                "cleaned_contexts": len(expired_contexts),
                "context_ids": expired_contexts
            }
        except Exception as e:
            logger.error(f"Error cleaning up contexts: {str(e)}")
            return {"status": "error", "error": str(e)} 
