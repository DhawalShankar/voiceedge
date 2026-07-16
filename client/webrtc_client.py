"""
webrtc_client.py
VoiceEdge Client - WebRTC Audio Client

Responsibility:
    - Register with the signaling server
    - Wait to be matched with a peer
    - Perform WebRTC offer/answer/ICE exchange (relayed through signaling server)
    - Capture local microphone audio and send it over the peer connection
    - Play back audio received from the peer

Usage:
    python client/webrtc_client.py --client-id laptop_A --signaling ws://<gateway-ip>:8765
    python client/webrtc_client.py --client-id laptop_B --signaling ws://<gateway-ip>:8765
"""

import argparse
import asyncio
import json
import logging

import numpy as np
import sounddevice as sd
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.media import MediaPlayer
from aiortc.mediastreams import MediaStreamTrack

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webrtc_client")

SAMPLE_RATE = 48000
CHANNELS = 1


class SpeakerAudioTrack:
    """
    Consumes frames from a remote audio track and plays them through
    the local speaker using sounddevice, since aiortc has no built-in
    speaker output.
    """

    def __init__(self, track: MediaStreamTrack):
        self.track = track
        self._stream = sd.OutputStream(
            samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="int16"
        )
        self._stream.start()
        self._task = asyncio.ensure_future(self._play())

    async def _play(self):
        try:
            while True:
                frame = await self.track.recv()
                pcm = frame.to_ndarray()
                # Ensure correct shape/dtype for playback
                pcm = pcm.astype(np.int16).reshape(-1, CHANNELS)
                self._stream.write(pcm)
        except Exception as e:
            logger.info(f"Playback stopped: {e}")

    def stop(self):
        self._task.cancel()
        self._stream.stop()
        self._stream.close()


class VoiceEdgeClient:
    def __init__(self, client_id: str, signaling_url: str):
        self.client_id = client_id
        self.signaling_url = signaling_url
        self.pc: RTCPeerConnection = None
        self.ws = None
        self.peer_id: str = None
        self.speaker_track: SpeakerAudioTrack = None

    async def run(self):
        async with websockets.connect(self.signaling_url) as ws:
            self.ws = ws
            await self._send({"type": "register", "client_id": self.client_id})
            logger.info(f"Registered as {self.client_id}, waiting for peer...")

            async for raw_message in ws:
                message = json.loads(raw_message)
                await self._handle_message(message)

    async def _handle_message(self, message: dict):
        msg_type = message.get("type")

        if msg_type == "waiting":
            logger.info("Waiting for a peer to join...")

        elif msg_type == "matched":
            self.peer_id = message["peer_id"]
            logger.info(f"Matched with peer: {self.peer_id}")
            await self._setup_peer_connection()
            if message["initiator"]:
                await self._create_offer()

        elif msg_type == "offer":
            await self._setup_peer_connection()
            await self.pc.setRemoteDescription(
                RTCSessionDescription(sdp=message["sdp"], type="offer")
            )
            answer = await self.pc.createAnswer()
            await self.pc.setLocalDescription(answer)
            await self._send({
                "type": "answer",
                "target_id": self.peer_id,
                "sdp": self.pc.localDescription.sdp,
            })

        elif msg_type == "answer":
            await self.pc.setRemoteDescription(
                RTCSessionDescription(sdp=message["sdp"], type="answer")
            )

        elif msg_type == "ice_candidate":
            candidate = message.get("candidate")
            if candidate:
                await self.pc.addIceCandidate(candidate)

    async def _setup_peer_connection(self):
        if self.pc is not None:
            return

        self.pc = RTCPeerConnection()

        # Capture microphone audio.
        # NOTE: device format is platform-specific.
        #   Windows: MediaPlayer("audio=<device name>", format="dshow")
        #   Linux:   MediaPlayer("default", format="pulse")
        #   macOS:   MediaPlayer(":0", format="avfoundation")
        player = MediaPlayer("audio=Microphone Array (AMD Audio Device)", format="dshow")
        if player.audio:
            self.pc.addTrack(player.audio)

        @self.pc.on("track")
        def on_track(track):
            logger.info(f"Receiving remote track: {track.kind}")
            if track.kind == "audio":
                self.speaker_track = SpeakerAudioTrack(track)

        @self.pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate:
                await self._send({
                    "type": "ice_candidate",
                    "target_id": self.peer_id,
                    "candidate": candidate.to_sdp(),
                })

    async def _create_offer(self):
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        await self._send({
            "type": "offer",
            "target_id": self.peer_id,
            "sdp": self.pc.localDescription.sdp,
        })

    async def _send(self, message: dict):
        await self.ws.send(json.dumps(message))


def main():
    parser = argparse.ArgumentParser(description="VoiceEdge WebRTC Client")
    parser.add_argument("--client-id", required=True, help="Unique client identifier")
    parser.add_argument(
        "--signaling", default="ws://localhost:8765", help="Signaling server URL"
    )
    args = parser.parse_args()

    client = VoiceEdgeClient(args.client_id, args.signaling)
    asyncio.run(client.run())


if __name__ == "__main__":
    main()