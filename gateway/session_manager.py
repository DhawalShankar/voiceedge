"""
session_manager.py
VoiceEdge Gateway - Session Manager (FR-3)

Responsibility:
    Track active communication sessions between clients.
    Each session represents one active call routed through the gateway.
"""

import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Session:
    session_id: str
    client_a_id: str
    client_b_id: str
    start_time: float = field(default_factory=time.time)
    status: str = "active"  # active | ended | on_hold

    def duration(self) -> float:
        return time.time() - self.start_time


class SessionManager:
    """
    Maintains the registry of all active sessions in the gateway.
    """

    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def create_session(self, client_a_id: str, client_b_id: str) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(
            session_id=session_id,
            client_a_id=client_a_id,
            client_b_id=client_b_id,
        )
        self._sessions[session_id] = session
        return session

    def end_session(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if session:
            session.status = "ended"
            del self._sessions[session_id]
            return True
        return False

    def get_session(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    def get_active_sessions(self) -> Dict[str, Session]:
        return {sid: s for sid, s in self._sessions.items() if s.status == "active"}

    def active_call_count(self) -> int:
        return len(self.get_active_sessions())

    def find_session_by_client(self, client_id: str) -> Optional[Session]:
        for session in self._sessions.values():
            if client_id in (session.client_a_id, session.client_b_id):
                return session
        return None


# Quick manual test when run directly
if __name__ == "__main__":
    sm = SessionManager()
    s1 = sm.create_session("laptop_A", "laptop_B")
    print(f"Session created: {s1.session_id}")
    print(f"Active calls: {sm.active_call_count()}")
    print(f"Duration so far: {s1.duration():.2f}s")

    sm.end_session(s1.session_id)
    print(f"Active calls after ending: {sm.active_call_count()}")