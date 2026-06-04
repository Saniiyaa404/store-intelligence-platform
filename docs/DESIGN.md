# DESIGN.md

# Store Intelligence Platform Design

## Overview

The system converts multi-camera retail CCTV footage into structured visitor events and business analytics.

The solution consists of three independent processing pipelines:

1. Entry Pipeline
2. Zone Pipeline
3. Billing Pipeline

Each pipeline generates JSONL events that are consumed by the analytics API and dashboard.

---

# System Architecture

Video Clips
    ↓

YOLOv8s Person Detection
    ↓

ByteTrack Multi-Object Tracking
    ↓

Event Generation

├── Entry Pipeline
│   ├── STORE_ENTER
│   └── STORE_EXIT
│
├── Zone Pipeline
│   ├── ZONE_ENTER
│   └── ZONE_EXIT
│
└── Billing Pipeline
    ├── QUEUE_ENTER
    ├── PURCHASE
    └── QUEUE_UPDATE

    ↓

events.jsonl

    ↓

FastAPI Analytics Layer

    ├── Metrics API
    ├── Funnel API
    ├── Heatmap API
    └── Anomaly API

    ↓

Streamlit Dashboard

---

# Entry Pipeline

Purpose:

Detect visitors entering and exiting the store.

Process:

1. Detect persons using YOLOv8s.
2. Track persons using ByteTrack.
3. Monitor movement relative to a configured entry line.
4. Generate:

- STORE_ENTER
- STORE_EXIT

events.

---

# Zone Pipeline

Purpose:

Measure visitor engagement across store sections.

Process:

1. Detect persons.
2. Track visitors.
3. Map visitor head coordinates to polygon zones.
4. Confirm zone presence across multiple frames.
5. Generate:

- ZONE_ENTER
- ZONE_EXIT

events.

Dwell time is calculated using frame timestamps.

---

# Billing Pipeline

Purpose:

Estimate purchases and queue behavior.

Process:

1. Detect visitors inside billing area.
2. Count queue occupancy.
3. Track queue dwell time.
4. Generate:

- QUEUE_ENTER
- PURCHASE
- QUEUE_UPDATE

events.

Purchase events are inferred when a visitor remains in queue beyond a configured threshold.

---

# Re-Identification

The system maintains global visitor identities across cameras.

Implementation:

- Appearance feature extraction using color histograms.
- Similarity matching between active tracks.
- Global visitor IDs.

Example:

Track 4 (Camera A)
→ VIS_12

Track 18 (Camera B)
→ VIS_12

This reduces visitor double-counting across cameras.

---

# Staff Exclusion

Staff traffic should not affect customer analytics.

Implementation:

Store staff are detected using appearance-based uniform recognition.

For Store 2:

- Pink/red uniform detection

Detected staff are excluded from:

- Visitor counts
- Funnel analytics
- Conversion metrics

---

# Analytics Layer

FastAPI provides analytics endpoints:

- /metrics/{store_id}
- /funnel/{store_id}
- /heatmap/{store_id}
- /anomalies/{store_id}

Analytics are computed directly from generated events.

---

# Dashboard

The Streamlit dashboard displays:

- Unique visitors
- Conversion rate
- Abandonment rate
- Queue depth
- Funnel metrics
- Zone heatmaps
- Business anomalies

The dashboard fetches data directly from FastAPI endpoints.

---

# AI-Assisted Decisions

## Decision 1: Re-Identification

AI suggested implementing lightweight appearance-based ReID rather than deploying a heavy deep-learning ReID model.

Suggested:

- Appearance matching
- Similarity scoring
- Global visitor identities

Implemented:

- Color histogram embeddings
- Similarity matching
- Global visitor IDs

Reason:

Provided cross-camera identity consistency while remaining feasible within hackathon constraints.

---

## Decision 2: Staff Exclusion

AI suggested using appearance-based uniform detection because labeled staff data was unavailable.

Implemented:

- Uniform color detection
- Staff filtering

Reason:

Reduced distortion in visitor metrics while avoiding the complexity of training a separate classifier.

---

## Decision 3: Dashboard Architecture

AI suggested exposing analytics through FastAPI and visualizing them using Streamlit.

Implemented:

- FastAPI analytics service
- Streamlit dashboard

Reason:

Enabled rapid development and demonstrated a production-style architecture.