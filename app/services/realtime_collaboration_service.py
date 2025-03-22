from typing import Dict, Any, List, Optional, Set
import logging
from datetime import datetime, timedelta
import asyncio
from fastapi import HTTPException, WebSocket
from collections import defaultdict
import json
import uuid

logger = logging.getLogger(__name__)

class RealtimeCollaborationService:
    def __init__(self):
        """Initialize the Realtime Collaboration Service."""
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_participants: Dict[str, Set[str]] = defaultdict(set)
        self.document_locks: Dict[str, str] = {}
        self.collaborative_documents: Dict[str, Dict[str, Any]] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
        self.document_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.pending_changes: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.session_metadata: Dict[str, Dict[str, Any]] = {}

    async def create_session(
        self,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Create a new collaboration session."""
        try:
            if session_id in self.active_sessions:
                raise HTTPException(status_code=400, detail="Session already exists")

            session = {
                "id": session_id,
                "creator": user_id,
                "created_at": datetime.now(),
                "status": "active",
                "participants": {user_id},
                "documents": [],
                "settings": self._get_default_session_settings()
            }

            self.active_sessions[session_id] = session
            self.session_participants[session_id].add(user_id)
            self.session_metadata[session_id] = {
                "last_activity": datetime.now(),
                "participant_status": {user_id: "active"},
                "session_type": "default"
            }

            return session
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def join_session(
        self,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Join an existing collaboration session."""
        try:
            if session_id not in self.active_sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            session = self.active_sessions[session_id]
            if user_id in session["participants"]:
                raise HTTPException(status_code=400, detail="User already in session")

            session["participants"].add(user_id)
            self.session_participants[session_id].add(user_id)
            self.session_metadata[session_id]["participant_status"][user_id] = "active"
            self.session_metadata[session_id]["last_activity"] = datetime.now()

            await self._broadcast_session_update(session_id, {
                "type": "participant_joined",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })

            return session
        except Exception as e:
            logger.error(f"Error joining session: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def leave_session(
        self,
        session_id: str,
        user_id: str
    ) -> None:
        """Leave a collaboration session."""
        try:
            if session_id not in self.active_sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            session = self.active_sessions[session_id]
            if user_id not in session["participants"]:
                raise HTTPException(status_code=400, detail="User not in session")

            session["participants"].remove(user_id)
            self.session_participants[session_id].remove(user_id)
            del self.session_metadata[session_id]["participant_status"][user_id]

            # Release any locks held by the user
            self._release_user_locks(session_id, user_id)

            await self._broadcast_session_update(session_id, {
                "type": "participant_left",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })

            # Clean up empty session
            if not session["participants"]:
                await self._cleanup_session(session_id)
        except Exception as e:
            logger.error(f"Error leaving session: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_session(
        self,
        session_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update session information."""
        try:
            if session_id not in self.active_sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            session = self.active_sessions[session_id]
            if user_id not in session["participants"]:
                raise HTTPException(status_code=403, detail="User not authorized")

            # Apply updates
            for key, value in updates.items():
                if key in ["settings", "status"]:
                    session[key] = value

            self.session_metadata[session_id]["last_activity"] = datetime.now()

            await self._broadcast_session_update(session_id, {
                "type": "session_updated",
                "user_id": user_id,
                "updates": updates,
                "timestamp": datetime.now().isoformat()
            })

            return session
        except Exception as e:
            logger.error(f"Error updating session: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def share_document(
        self,
        session_id: str,
        user_id: str,
        document_id: str,
        document_content: str
    ) -> Dict[str, Any]:
        """Share a document in the session."""
        try:
            if session_id not in self.active_sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            session = self.active_sessions[session_id]
            if user_id not in session["participants"]:
                raise HTTPException(status_code=403, detail="User not authorized")

            document = {
                "id": document_id,
                "content": document_content,
                "owner": user_id,
                "created_at": datetime.now(),
                "last_modified": datetime.now(),
                "version": 1,
                "status": "active"
            }

            self.collaborative_documents[document_id] = document
            session["documents"].append(document_id)
            self.document_history[document_id].append({
                "version": 1,
                "content": document_content,
                "user_id": user_id,
                "timestamp": datetime.now()
            })

            await self._broadcast_session_update(session_id, {
                "type": "document_shared",
                "document_id": document_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })

            return document
        except Exception as e:
            logger.error(f"Error sharing document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_document(
        self,
        session_id: str,
        document_id: str
    ) -> Dict[str, Any]:
        """Get a shared document."""
        try:
            if session_id not in self.active_sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            if document_id not in self.collaborative_documents:
                raise HTTPException(status_code=404, detail="Document not found")

            document = self.collaborative_documents[document_id]
            document["history"] = self.document_history[document_id]
            document["lock_status"] = self._get_document_lock_status(document_id)

            return document
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def lock_document(
        self,
        session_id: str,
        user_id: str,
        document_id: str
    ) -> None:
        """Lock a document for editing."""
        try:
            if session_id not in self.active_sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            if document_id in self.document_locks:
                if self.document_locks[document_id] != user_id:
                    raise HTTPException(status_code=400, detail="Document already locked")
                return

            self.document_locks[document_id] = user_id

            await self._broadcast_session_update(session_id, {
                "type": "document_locked",
                "document_id": document_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error locking document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def unlock_document(
        self,
        session_id: str,
        user_id: str,
        document_id: str
    ) -> None:
        """Unlock a document."""
        try:
            if session_id not in self.active_sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            if document_id not in self.document_locks:
                return

            if self.document_locks[document_id] != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to unlock")

            del self.document_locks[document_id]

            await self._broadcast_session_update(session_id, {
                "type": "document_unlocked",
                "document_id": document_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error unlocking document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def edit_document(
        self,
        session_id: str,
        user_id: str,
        document_id: str,
        document_content: str
    ) -> Dict[str, Any]:
        """Edit a shared document."""
        try:
            if session_id not in self.active_sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            if document_id not in self.collaborative_documents:
                raise HTTPException(status_code=404, detail="Document not found")

            if document_id in self.document_locks and self.document_locks[document_id] != user_id:
                raise HTTPException(status_code=403, detail="Document is locked")

            document = self.collaborative_documents[document_id]
            document["content"] = document_content
            document["last_modified"] = datetime.now()
            document["version"] += 1

            self.document_history[document_id].append({
                "version": document["version"],
                "content": document_content,
                "user_id": user_id,
                "timestamp": datetime.now()
            })

            await self._broadcast_session_update(session_id, {
                "type": "document_edited",
                "document_id": document_id,
                "user_id": user_id,
                "version": document["version"],
                "timestamp": datetime.now().isoformat()
            })

            return document
        except Exception as e:
            logger.error(f"Error editing document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def review_document(
        self,
        session_id: str,
        user_id: str,
        document_id: str
    ) -> Dict[str, Any]:
        """Review a shared document."""
        try:
            if session_id not in self.active_sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            if document_id not in self.collaborative_documents:
                raise HTTPException(status_code=404, detail="Document not found")

            document = self.collaborative_documents[document_id]
            review_data = {
                "document_id": document_id,
                "reviewer": user_id,
                "timestamp": datetime.now(),
                "version": document["version"],
                "history": self.document_history[document_id],
                "pending_changes": self.pending_changes[document_id]
            }

            await self._broadcast_session_update(session_id, {
                "type": "document_review",
                "document_id": document_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })

            return review_data
        except Exception as e:
            logger.error(f"Error reviewing document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    # Helper methods
    def _get_default_session_settings(self) -> Dict[str, Any]:
        """Get default session settings."""
        return {
            "max_participants": 10,
            "auto_lock_timeout": 300,  # 5 minutes
            "require_approval": True,
            "track_changes": True,
            "allow_anonymous": False
        }

    def _release_user_locks(self, session_id: str, user_id: str) -> None:
        """Release all document locks held by a user."""
        for doc_id, lock_holder in list(self.document_locks.items()):
            if lock_holder == user_id:
                del self.document_locks[doc_id]

    async def _cleanup_session(self, session_id: str) -> None:
        """Clean up an empty session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        if session_id in self.session_participants:
            del self.session_participants[session_id]
        if session_id in self.session_metadata:
            del self.session_metadata[session_id]

    def _get_document_lock_status(self, document_id: str) -> Dict[str, Any]:
        """Get the lock status of a document."""
        return {
            "locked": document_id in self.document_locks,
            "locked_by": self.document_locks.get(document_id),
            "locked_at": datetime.now() if document_id in self.document_locks else None
        }

    async def _broadcast_session_update(
        self,
        session_id: str,
        update_data: Dict[str, Any]
    ) -> None:
        """Broadcast an update to all session participants."""
        if session_id in self.session_participants:
            for user_id in self.session_participants[session_id]:
                if user_id in self.websocket_connections:
                    try:
                        await self.websocket_connections[user_id].send_json(update_data)
                    except Exception as e:
                        logger.error(f"Error broadcasting to user {user_id}: {str(e)}")

    async def register_websocket(
        self,
        user_id: str,
        websocket: WebSocket
    ) -> None:
        """Register a WebSocket connection for a user."""
        self.websocket_connections[user_id] = websocket

    async def unregister_websocket(
        self,
        user_id: str
    ) -> None:
        """Unregister a WebSocket connection."""
        if user_id in self.websocket_connections:
            del self.websocket_connections[user_id] 
