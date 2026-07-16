"""
media_router.py
VoiceEdge Gateway - Media Router (FR-2)

Responsibility:
    Ensure all audio frames pass through the gateway before reaching
    the destination client. This is where future plugins (translation,
    enhancement, etc.) will hook into the audio stream.

Design:
    Each active call session gets a MediaRoute, which forwards audio
    frames from sender to receiver. The router calls into the plugin
    interface (currently a passthrough) before delivering audio.
"""

import time
from typing import Callable, Dict, Optional
from gateway.session_manager import Session


class MediaRoute:
    """
    Represents one direction (or bidirectional pair) of audio flow
    tied to a session. Tracks basic per-route counters used later
    by the metrics engine.
    """

    def __init__(self, session: Session, on_deliver: Callable[[str, bytes], None]):
        self.session = session
        self.on_deliver = on_deliver  # callback: (destination_client_id, audio_frame)
        self.frames_routed = 0
        self.bytes_routed = 0
        self.last_frame_time: Optional[float] = None

    def route_frame(self, sender_id: str, audio_frame: bytes) -> None:
        """
        Route a single audio frame from sender to the other party
        in the session. This is the single choke point all media
        must pass through (FR-2).
        """
        destination = (
            self.session.client_b_id
            if sender_id == self.session.client_a_id
            else self.session.client_a_id
        )

        # Placeholder for future plugin hook:
        # audio_frame = plugin_manager.process(audio_frame)

        self.on_deliver(destination, audio_frame)

        self.frames_routed += 1
        self.bytes_routed += len(audio_frame)
        self.last_frame_time = time.time()


class MediaRouter:
    """
    Owns all active MediaRoutes, keyed by session_id.
    """

    def __init__(self):
        self._routes: Dict[str, MediaRoute] = {}

    def create_route(
        self, session: Session, on_deliver: Callable[[str, bytes], None]
    ) -> MediaRoute:
        route = MediaRoute(session, on_deliver)
        self._routes[session.session_id] = route
        return route

    def remove_route(self, session_id: str) -> bool:
        if session_id in self._routes:
            del self._routes[session_id]
            return True
        return False

    def route_frame(self, session_id: str, sender_id: str, audio_frame: bytes) -> bool:
        route = self._routes.get(session_id)
        if not route:
            return False
        route.route_frame(sender_id, audio_frame)
        return True

    def get_route_stats(self, session_id: str) -> Optional[dict]:
        route = self._routes.get(session_id)
        if not route:
            return None
        return {
            "frames_routed": route.frames_routed,
            "bytes_routed": route.bytes_routed,
            "last_frame_time": route.last_frame_time,
        }


# Quick manual test when run directly
if __name__ == "__main__":
    from gateway.session_manager import SessionManager

    sm = SessionManager()
    session = sm.create_session("laptop_A", "laptop_B")

    router = MediaRouter()

    def fake_deliver(destination_id: str, frame: bytes):
        print(f"Delivered {len(frame)} bytes -> {destination_id}")

    router.create_route(session, fake_deliver)

    # Simulate laptop_A sending 3 fake audio frames
    for i in range(3):
        fake_audio = b"\x00" * 160  # e.g. 160-byte PCM frame
        router.route_frame(session.session_id, "laptop_A", fake_audio)

    print("Stats:", router.get_route_stats(session.session_id))