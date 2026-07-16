"""
signaling_server.py
VoiceEdge Gateway - Signaling Server

Responsibility:
    Handle the WebRTC signaling handshake between two clients:
        - Exchange SDP offers/answers
        - Exchange ICE candidates
        - Notify gateway to create a Session once both clients are matched

    This uses websockets as a simple signaling transport. The actual
    audio media itself does NOT flow through this server - only the
    connection setup metadata does. Once WebRTC connects, audio flows
    through the gateway's MediaRouter (media_router.py).
"""

import asyncio
import json
import logging
from typing import Dict

import websockets

from gateway.session_manager import SessionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("signaling_server")


class SignalingServer:
    def __init__(self, session_manager: SessionManager, host: str = "0.0.0.0", port: int = 8765):
        self.session_manager = session_manager
        self.host = host
        self.port = port
        # client_id -> websocket connection
        self.clients: Dict[str, object] = {}
        # simple waiting-room: first client waits here until a second joins
        self.waiting_client_id: str = None

    async def handler(self, websocket):
        client_id = None
        try:
            async for raw_message in websocket:
                message = json.loads(raw_message)
                msg_type = message.get("type")

                if msg_type == "register":
                    client_id = message["client_id"]
                    self.clients[client_id] = websocket
                    logger.info(f"Client registered: {client_id}")
                    await self._try_match(client_id)

                elif msg_type in ("offer", "answer", "ice_candidate"):
                    await self._relay(message)

                else:
                    logger.warning(f"Unknown message type: {msg_type}")

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        finally:
            if client_id and client_id in self.clients:
                del self.clients[client_id]
            if self.waiting_client_id == client_id:
                self.waiting_client_id = None

    async def _try_match(self, client_id: str) -> None:
        """
        Simple pairing logic: first client waits, second client
        triggers session creation and both are notified.
        """
        if self.waiting_client_id is None:
            self.waiting_client_id = client_id
            await self._send(client_id, {"type": "waiting"})
            return

        peer_id = self.waiting_client_id
        self.waiting_client_id = None

        session = self.session_manager.create_session(peer_id, client_id)
        logger.info(f"Session created: {session.session_id} ({peer_id} <-> {client_id})")

        # Tell the first (waiting) client to initiate the offer
        await self._send(peer_id, {
            "type": "matched",
            "session_id": session.session_id,
            "peer_id": client_id,
            "initiator": True,
        })
        # Tell the second client to expect an offer
        await self._send(client_id, {
            "type": "matched",
            "session_id": session.session_id,
            "peer_id": peer_id,
            "initiator": False,
        })

    async def _relay(self, message: dict) -> None:
        """Forward offer/answer/ICE candidates to the intended peer."""
        target_id = message.get("target_id")
        if target_id and target_id in self.clients:
            await self._send(target_id, message)
        else:
            logger.warning(f"Relay failed - unknown target: {target_id}")

    async def _send(self, client_id: str, message: dict) -> None:
        websocket = self.clients.get(client_id)
        if websocket:
            await websocket.send(json.dumps(message))

    async def start(self) -> None:
        logger.info(f"Signaling server starting on ws://{self.host}:{self.port}")
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()  # run forever


if __name__ == "__main__":
    session_manager = SessionManager()
    server = SignalingServer(session_manager)
    asyncio.run(server.start())