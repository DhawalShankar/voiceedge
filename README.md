# VoiceEdge

**A Programmable VoIP Media Gateway with Embedded Network Management Console**

Electronics & Communication Engineering | Major Project | Two Semesters

---

## What is this?

VoiceEdge is a lab-scale prototype of a **programmable media gateway** — instead of
two people talking directly over WebRTC, their voice traffic is routed **through**
a central gateway process. This makes it possible to later plug in real-time
speech-processing services (translation, noise suppression, accessibility features,
etc.) **without redesigning the communication architecture**.

Full requirements and design rationale: [`docs/Major-Project-PRD.md`](docs/Major-Project-PRD.md)

---

## Current Status (Semester 1)

| Component | Status |
|---|---|
| Session Manager (FR-3) | ✅ Implemented & tested |
| Media Router (FR-2) | ✅ Implemented & tested |
| Metrics Engine (FR-5) | ✅ Implemented & tested |
| Signaling Server (WebRTC handshake) | ✅ Implemented & tested (starts cleanly) |
| WebRTC Client (mic capture/playback) | 🟡 Written, NOT yet run/tested end-to-end |
| Serial Bridge (Arduino comms, FR-6) | 🔲 Deferred |
| Embedded Console (Arduino, FR-7/FR-8) | 🔲 Deferred — hardware phase later |
| Plugin Interface (FR-9) | 🔲 Placeholder only (by design, Sem 1) |

> **Note:** The Arduino/embedded hardware console is intentionally deferred.
> The focus right now is getting the software gateway (session handling,
> audio routing, metrics, signaling) working and tested end-to-end between
> two clients. Hardware integration will follow once this is stable.

---

## TODO

### ✅ Done
- [x] Project structure created
- [x] `session_manager.py` — written and tested standalone
- [x] `media_router.py` — written and tested standalone
- [x] `metrics_engine.py` — written and tested standalone (uses `psutil`)
- [x] `signaling_server.py` — written, starts cleanly, listens on port 8765
- [x] `webrtc_client.py` — written (mic capture via `aiortc.MediaPlayer`, speaker playback via `sounddevice`)
- [x] ffmpeg installed on Windows dev machine, confirmed working
- [x] Microphone device identified: `Microphone Array (AMD Audio Device)` — plugged into client code

### 🔲 To Do Next
- [ ] Run signaling server + two client instances (`laptop_A`, `laptop_B`) and verify handshake completes
- [ ] Debug any mic access conflicts when running two clients on the same machine
- [ ] Verify actual audio is heard on both ends (currently untested)
- [ ] Test across two separate laptops on same Wi-Fi (matches real PRD scenario, not just localhost)
- [ ] Add `logger.py` — persistent communication logs (FR-4)
- [ ] Add `serial_bridge.py` — Arduino serial communication (FR-6) — **deferred to hardware phase**
- [ ] Write `plugin_base.py` interface stub properly (FR-9) — placeholder currently empty
- [ ] Add unit tests in `tests/` folder for each module (currently only manual `__main__` tests exist)
- [ ] Write `scripts/setup_env.sh` / equivalent `.ps1` for one-command environment setup
- [ ] Update this README once client is confirmed working end-to-end

---

## Project Structure

```
voiceedge/
├── docs/                     # PRD and design docs
├── client/                   # WebRTC client code (mic capture, playback)
├── gateway/                  # Core gateway logic
│   ├── session_manager.py    # Tracks active call sessions (FR-3)
│   ├── media_router.py       # Routes audio through the gateway (FR-2)
│   ├── metrics_engine.py     # Latency, packets, CPU/mem, uptime (FR-5)
│   ├── signaling_server.py   # WebRTC offer/answer/ICE exchange
│   ├── serial_bridge.py      # (deferred) Arduino serial comms
│   ├── logger.py             # Communication logs (FR-4)
│   └── plugins/              # Plugin interface (placeholder, Sem 1)
├── embedded/                 # (deferred) Arduino sketch + headers
├── tests/                    # Unit tests
└── scripts/                  # Setup/run helper scripts
```

---

## Setup

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install aiortc websockets pyserial numpy sounddevice psutil

# Freeze dependencies
pip freeze > requirements.txt
```

---

## Running & Testing Individual Modules

Each core module can be tested standalone:

```powershell
# Session Manager
python gateway\session_manager.py

# Media Router (module import, run from project root)
python -m gateway.media_router

# Metrics Engine
python -m gateway.metrics_engine

# Signaling Server (runs forever - Ctrl+C to stop)
python -m gateway.signaling_server
```

---

## Architecture

```
Laptop A (WebRTC Client)
        │
        ▼
────────────────────────
     VoiceEdge Gateway
────────────────────────
 Session Manager
 Media Router
 Metrics Engine
 Plugin Manager (interface only)
 Serial Communication Module (deferred)
────────────────────────
        │
        ▼
Laptop B (WebRTC Client)

        │
   USB Serial (deferred)
        │
        ▼
Embedded Network Management Console (Arduino)
```

---

## Roadmap

**Semester 1:** VoIP gateway core, session management, media routing, metrics,
signaling — all software, no hardware, no AI processing.

**Semester 2:** Translation plugin, dynamic plugin loading, embedded Arduino
console, Raspberry Pi deployment (optional).

See full details in [`docs/Major-Project-PRD.md`](docs/Major-Project-PRD.md).