"""
metrics_engine.py
VoiceEdge Gateway - Metrics Engine (FR-5)

Responsibility:
    Continuously compute and expose gateway health/performance metrics:
        - Latency (ms)
        - Packet count
        - Active calls
        - Uptime
        - CPU usage
        - Memory usage

    These metrics are later transmitted to the Arduino console (FR-6)
    and can be exposed via an API/log for debugging.
"""

import time
import psutil
from dataclasses import dataclass, field


@dataclass
class GatewayMetrics:
    start_time: float = field(default_factory=time.time)
    total_packets_routed: int = 0
    total_bytes_routed: int = 0
    last_latency_ms: float = 0.0

    def uptime_seconds(self) -> float:
        return time.time() - self.start_time


class MetricsEngine:
    """
    Central metrics computation. Pulls live data from SessionManager
    and MediaRouter, plus system-level stats via psutil.
    """

    def __init__(self, session_manager, media_router):
        self.session_manager = session_manager
        self.media_router = media_router
        self.metrics = GatewayMetrics()

    def record_frame_latency(self, latency_ms: float) -> None:
        """Call this whenever a frame's send->receive latency is measured."""
        self.metrics.last_latency_ms = latency_ms

    def record_packet(self, size_bytes: int) -> None:
        self.metrics.total_packets_routed += 1
        self.metrics.total_bytes_routed += size_bytes

    def snapshot(self) -> dict:
        """
        Returns a full metrics snapshot - this is what gets sent
        to the Arduino (FR-6) and/or logged/displayed.
        """
        return {
            "active_calls": self.session_manager.active_call_count(),
            "latency_ms": round(self.metrics.last_latency_ms, 2),
            "total_packets": self.metrics.total_packets_routed,
            "total_bytes": self.metrics.total_bytes_routed,
            "uptime_seconds": round(self.metrics.uptime_seconds(), 1),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
        }

    def health_status(self) -> str:
        """
        Simple health classification, used later to drive the
        Arduino LED indicators (green/blue/yellow/red).
        """
        snap = self.snapshot()
        if snap["cpu_percent"] > 90 or snap["memory_percent"] > 90:
            return "FAULT"
        if snap["latency_ms"] > 150:
            return "HIGH_LATENCY"
        if snap["active_calls"] > 0:
            return "ACTIVE_CALL"
        return "HEALTHY"


# Quick manual test when run directly
if __name__ == "__main__":
    from gateway.session_manager import SessionManager
    from gateway.media_router import MediaRouter

    sm = SessionManager()
    mr = MediaRouter()
    session = sm.create_session("laptop_A", "laptop_B")

    engine = MetricsEngine(sm, mr)
    engine.record_packet(160)
    engine.record_packet(160)
    engine.record_frame_latency(42.5)

    print("Snapshot:", engine.snapshot())
    print("Health:", engine.health_status())