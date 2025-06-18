from datetime import datetime
from typing import List, Dict
import uuid

class ChatSessionManager:
    """Manage chat sessions and history"""
    
    def __init__(self):
        self.sessions = {}
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session"""
        return self.sessions.get(session_id, [])
    
    def add_to_session(self, session_id: str, user_query: str, bot_response: str):
        """Add interaction to session history"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append({
            "user": user_query,
            "bot": bot_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 10 interactions
        if len(self.sessions[session_id]) > 10:
            self.sessions[session_id] = self.sessions[session_id][-10:]

    def create_session(self) -> str:
        """Create a new chat session and return its ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        return session_id
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        return session_id in self.sessions
    
    def delete_session(self, session_id: str):
        """Delete a chat session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        else:
            raise ValueError("Session not found")
        
    def clear_all_sessions(self):
        """Clear all chat sessions"""
        self.sessions.clear()
        print("All chat sessions cleared.")

    def get_all_sessions(self) -> Dict[str, List[Dict]]:
        """Get all chat sessions and their histories"""
        return self.sessions
