from collections import deque
from src.monitoring.logger import logger

class ConversationMemory:
    def __init__(self, max_turns=5):
        # Dictionary mapping session_id to a deque of messages
        self.sessions = {}
        self.max_turns = max_turns

    def add_message(self, session_id, role, content):
        if session_id not in self.sessions:
            self.sessions[session_id] = deque(maxlen=self.max_turns * 2)
        
        self.sessions[session_id].append({"role": role, "content": content})
        logger.info(f"Memory updated for session {session_id}: {role}")

    def get_history(self, session_id):
        return list(self.sessions.get(session_id, []))

    def format_history(self, session_id):
        history = self.get_history(session_id)
        if not history:
            return ""
        
        formatted = "Recent Conversation History:\n"
        for msg in history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            formatted += f"{role}: {msg['content']}\n"
        return formatted

memory = ConversationMemory()
