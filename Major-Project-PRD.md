# Major-Project-PRD.md

# VoiceEdge

## A Programmable VoIP Media Gateway with Embedded Network Management Console

**Version:** 1.0

**Department:** Electronics & Communication Engineering

**Project Duration:** Two Semesters

**Primary Language:** Python

---

## Vision

**VoiceEdge aims to decouple advanced communication capabilities from end-user device hardware by providing a programmable media-processing layer within the communication network.**

The system implements a laboratory-scale VoIP media gateway through which real-time voice traffic is routed before reaching the receiver. This gateway provides a programmable architecture in which additional communication services—such as noise suppression, translation, speech enhancement, and accessibility assistance—can be deployed as independent network-side modules.

The long-term vision is to enable advanced communication experiences even on low-cost or legacy devices whose hardware may not support such processing locally.

> **The device provides connectivity; the network provides intelligence.**


---

# 2. Problem Statement

Current communication applications perform most advanced processing on client devices or inside proprietary cloud infrastructure.

This project proposes a laboratory-scale prototype of a programmable communication gateway where all media passes through a central processing node before reaching the receiver.

Instead of focusing on a single AI feature, the project focuses on designing the communication infrastructure that can host future speech-processing services.

---

# 3. Project Objectives

* Build a real-time VoIP communication gateway.
* Route all voice traffic through a central node.
* Design a future-proof plugin architecture.
* Develop an embedded hardware management console.
* Measure communication metrics.
* Demonstrate gateway management through hardware controls.

---

# 4. Scope

## Semester 1

* VoIP communication
* Gateway implementation
* Session management
* Network metrics
* Embedded management console
* Plugin framework (placeholder only)

## Semester 2

* Translation plugin
* Additional speech-processing plugins
* Plugin loading
* Raspberry Pi deployment (optional)

---

# 5. System Architecture

```text
                    Wi-Fi

Laptop A
     │
     ▼

WebRTC Client

     │

────────────────────────────────────

        VoiceEdge Gateway

────────────────────────────────────

Session Manager

Media Router

Metrics Engine

Plugin Manager

(Plugin Interface Only)

Serial Communication Module

────────────────────────────────────

     │

WebRTC Client

     ▼

Laptop B


          │

     USB Serial

          │

          ▼

Embedded Network
Management Console

(Arduino)
```

---

# 6. Major Components

## 6.1 WebRTC Clients

Responsibilities

* Capture microphone
* Send voice
* Receive voice
* Play received audio

---

## 6.2 VoiceEdge Gateway

Responsibilities

* Accept calls
* Route audio
* Manage sessions
* Measure metrics
* Expose plugin interface
* Communicate with Arduino

---

## 6.3 Embedded Network Management Console

Hardware

* Arduino Uno
* OLED Display
* LEDs
* Push Buttons

Responsibilities

* Display gateway status
* Display active calls
* Display latency
* Display packet statistics
* Gateway ON/OFF
* Maintenance mode
* Future plugin switching

---

# 7. Functional Requirements

## FR-1

Two clients shall communicate in real time.

---

## FR-2

All media shall pass through the VoiceEdge Gateway.

---

## FR-3

Gateway shall maintain active communication sessions.

---

## FR-4

Gateway shall maintain communication logs.

---

## FR-5

Gateway shall continuously compute

* Latency
* Packet count
* Active calls
* Uptime
* CPU usage
* Memory usage

---

## FR-6

Gateway shall transmit metrics to Arduino through Serial communication.

---

## FR-7

Arduino shall display

* Gateway status
* Active calls
* Latency
* Packet statistics
* Current mode

---

## FR-8

Arduino shall provide hardware controls.

Buttons

* Start Gateway
* Stop Gateway
* Restart Gateway
* Maintenance Mode

Future

* Enable Plugin
* Disable Plugin

---

## FR-9

Plugin framework shall exist but remain unimplemented during Semester 1.

Example structure

```text
plugins/

    plugin.py

    README.md
```

---

# 8. Non-Functional Requirements

Latency

Gateway shall introduce minimal additional delay.

Availability

Gateway shall continue operating even if future plugins fail.

Scalability

New plugins shall not require gateway redesign.

Maintainability

Plugin interface shall remain generic.

Portability

Gateway shall execute on Linux-based systems.

---

# 9. Semester Plan

## Semester 1

### Deliverables

* WebRTC communication
* VoiceEdge Gateway
* Session manager
* Media router
* Metrics engine
* Arduino management console
* Plugin interface
* Technical documentation

No AI processing.

No translation.

No speech enhancement.

---

## Semester 2

### Deliverables

* Translation plugin
* Dynamic plugin loading
* Plugin management
* Evaluation metrics
* Raspberry Pi deployment (if available)
* Additional speech-processing modules

---

# 10. Embedded Network Management Console

Purpose

Provide a dedicated hardware interface for operating and monitoring the gateway.

Unlike the communication clients, this console represents the perspective of a network administrator.

Example OLED Display

```
VOICEEDGE

Gateway : ON

Calls : 02

Latency : 37 ms

Plugin : NONE

Status : HEALTHY
```

LED Indicators

Green

Gateway operational.

Blue

Active communication session.

Yellow

High latency.

Red

Gateway fault.

---

# 11. Future Plugin Architecture

Semester 1

Only interface.

```
Plugin

↓

process(audio)

↓

audio
```

Semester 2

Possible implementations

* Translation
* Speech Enhancement
* Accessibility
* Voice Anonymization
* Call Recording
* Scam Detection
* Call Summarization

---

# 12. Technology Stack

Language

* Python

Communication

* WebRTC

Networking

* UDP
* RTP (through WebRTC)

Embedded

* Arduino Uno

Communication with Arduino

* USB Serial

Development

* VS Code
* Git
* GitHub

---

# 13. Success Criteria

Semester 1

* Two laptops communicate successfully.
* Every audio stream passes through the gateway.
* Gateway metrics are computed correctly.
* Arduino displays gateway status.
* Arduino hardware controls operate correctly.
* Plugin interface exists.

Semester 2

* Translation plugin integrates successfully.
* Plugin can be enabled without changing gateway architecture.
* Gateway continues functioning if plugin is disabled.

---

# 14. Future Scope

The proposed architecture can support future speech-processing services such as:

* Real-time translation
* Noise suppression
* Speech enhancement
* Accessibility services
* Voice anonymization
* Intelligent call analytics

without modifying the communication clients.

---

# 15. Novelty

The primary contribution of this project is **not** a speech-processing algorithm.

The novelty lies in the design and implementation of a **programmable in-network media gateway** with an **embedded network management console**, enabling future speech-processing capabilities to be integrated as independent modules while preserving the underlying communication architecture.
