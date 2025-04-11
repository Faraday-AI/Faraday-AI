from typing import Dict, List, Set, Optional, Callable
from datetime import datetime
import markdown
import os
import json

class ActivityCollaborationManager:
    def __init__(self):
        self.collaborative_sessions = {}
        self.chat_messages = {}
        self.shared_filters = {}
        self.shared_sorts = {}
        self.annotations = {}
        self.real_time_updates = {}
        self.update_callbacks = {}
        self.version_history = {}
        
        # Initialize collaboration settings
        self.collaboration_settings = {
            'max_participants': 10,
            'session_timeout': 3600,  # 1 hour in seconds
            'max_chat_history': 1000,
            'auto_save_interval': 300  # 5 minutes in seconds
        }
        
        # Set up export directory for collaboration data
        self.export_dir = "exports/collaboration"
        os.makedirs(self.export_dir, exist_ok=True)

    async def start_collaborative_session(self, session_id: str, participants: List[str]) -> Dict:
        """Start a new collaborative session."""
        if len(participants) > self.collaboration_settings['max_participants']:
            raise ValueError(f"Maximum number of participants ({self.collaboration_settings['max_participants']}) exceeded")
            
        self.collaborative_sessions[session_id] = {
            'participants': set(participants),
            'chat_messages': [],
            'filters': {},
            'sorts': {},
            'annotations': [],
            'version': 0,
            'last_update': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        return self.collaborative_sessions[session_id]

    async def add_chat_message(self, session_id: str, user_id: str, message: str) -> Dict:
        """Add a chat message with markdown support."""
        if session_id not in self.collaborative_sessions:
            raise ValueError(f"Session {session_id} not found")
            
        if user_id not in self.collaborative_sessions[session_id]['participants']:
            raise ValueError(f"User {user_id} is not a participant in session {session_id}")
            
        chat_message = {
            'user_id': user_id,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'markdown': markdown.markdown(message)
        }
        
        self.collaborative_sessions[session_id]['chat_messages'].append(chat_message)
        
        # Trim chat history if needed
        if len(self.collaborative_sessions[session_id]['chat_messages']) > self.collaboration_settings['max_chat_history']:
            self.collaborative_sessions[session_id]['chat_messages'] = self.collaborative_sessions[session_id]['chat_messages'][-self.collaboration_settings['max_chat_history']:]
            
        return chat_message

    async def update_shared_filter(self, session_id: str, user_id: str, filter_data: dict) -> Dict:
        """Update shared filter settings."""
        if session_id not in self.collaborative_sessions:
            raise ValueError(f"Session {session_id} not found")
            
        if user_id not in self.collaborative_sessions[session_id]['participants']:
            raise ValueError(f"User {user_id} is not a participant in session {session_id}")
            
        self.collaborative_sessions[session_id]['filters'][user_id] = filter_data
        self.collaborative_sessions[session_id]['last_update'] = datetime.now().isoformat()
        
        return filter_data

    async def update_shared_sort(self, session_id: str, user_id: str, sort_data: dict) -> Dict:
        """Update shared sort settings."""
        if session_id not in self.collaborative_sessions:
            raise ValueError(f"Session {session_id} not found")
            
        if user_id not in self.collaborative_sessions[session_id]['participants']:
            raise ValueError(f"User {user_id} is not a participant in session {session_id}")
            
        self.collaborative_sessions[session_id]['sorts'][user_id] = sort_data
        self.collaborative_sessions[session_id]['last_update'] = datetime.now().isoformat()
        
        return sort_data

    async def add_annotation(self, session_id: str, user_id: str, annotation_data: dict) -> Dict:
        """Add a collaborative annotation."""
        if session_id not in self.collaborative_sessions:
            raise ValueError(f"Session {session_id} not found")
            
        if user_id not in self.collaborative_sessions[session_id]['participants']:
            raise ValueError(f"User {user_id} is not a participant in session {session_id}")
            
        annotation = {
            'user_id': user_id,
            'data': annotation_data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.collaborative_sessions[session_id]['annotations'].append(annotation)
        self.collaborative_sessions[session_id]['last_update'] = datetime.now().isoformat()
        
        return annotation

    async def subscribe_to_updates(self, session_id: str, callback: Callable) -> None:
        """Subscribe to real-time updates for a session."""
        if session_id not in self.update_callbacks:
            self.update_callbacks[session_id] = []
        self.update_callbacks[session_id].append(callback)

    async def create_version(self, session_id: str, data: dict) -> Dict:
        """Create a new version of the session data."""
        if session_id not in self.collaborative_sessions:
            raise ValueError(f"Session {session_id} not found")
            
        version = self.collaborative_sessions[session_id]['version'] + 1
        self.collaborative_sessions[session_id]['version'] = version
        
        version_data = {
            'version': version,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'created_by': self.collaborative_sessions[session_id]['participants']
        }
        
        self.version_history[f"{session_id}_{version}"] = version_data
        
        return version_data

    async def export_session_data(self, session_id: str) -> str:
        """Export session data to a file."""
        if session_id not in self.collaborative_sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session_data = {
            'session_info': self.collaborative_sessions[session_id],
            'chat_history': self.collaborative_sessions[session_id]['chat_messages'],
            'filters': self.collaborative_sessions[session_id]['filters'],
            'sorts': self.collaborative_sessions[session_id]['sorts'],
            'annotations': self.collaborative_sessions[session_id]['annotations'],
            'version_history': {k: v for k, v in self.version_history.items() if k.startswith(session_id)}
        }
        
        output_path = os.path.join(self.export_dir, f"{session_id}_export.json")
        
        with open(output_path, 'w') as f:
            json.dump(session_data, f, indent=2)
            
        return output_path

    async def cleanup_old_sessions(self) -> None:
        """Clean up old sessions that have timed out."""
        current_time = datetime.now()
        
        for session_id, session in list(self.collaborative_sessions.items()):
            last_update = datetime.fromisoformat(session['last_update'])
            if (current_time - last_update).total_seconds() > self.collaboration_settings['session_timeout']:
                # Export session data before cleanup
                await self.export_session_data(session_id)
                del self.collaborative_sessions[session_id]
                if session_id in self.update_callbacks:
                    del self.update_callbacks[session_id] 