# Store Intelligence Platform

A multi-camera retail analytics system that converts CCTV footage into structured visitor events and real-time business insights.

The solution performs:

- Person detection
- Multi-object tracking
- Store entry/exit detection
- Zone analytics
- Queue monitoring
- Purchase inference
- Staff exclusion
- Cross-camera visitor Re-Identification (ReID)
- Real-time analytics API
- Live dashboard visualization

---

# Architecture

Video Clips
    ↓
YOLOv8s Detection
    ↓
ByteTrack Tracking
    ↓

Entry Pipeline
 ├── STORE_ENTER
 └── STORE_EXIT

Zone Pipeline
 ├── ZONE_ENTER
 └── ZONE_EXIT

Billing Pipeline
 ├── QUEUE_ENTER
 ├── PURCHASE
 └── QUEUE_UPDATE

    ↓

events.jsonl

    ↓

FastAPI Analytics API

    ↓

Streamlit Dashboard

---

# Repository Structure

store-intelligence/

├── app/
│   ├── main.py
│   ├── ingestion.py
│   ├── metrics.py
│   ├── funnel.py
|   ├── health.py
│   ├── constants.py
│   ├── database.py
│   ├── models.py
│   ├── heatmap.py
│   └── anomalies.py
│
├── pipeline/
|   ├── config.py
│   ├── tracker.py
│   ├── run_entry.py
│   ├── run_zone.py
│   ├── run_billing.py
│   ├── reid.py
|   |── run.py
│   ├── staff.py
│   ├── detect.py
│   ├── tracker.py
│   ├── events.py
│   |── events.jsonl
|   ├── zones.py
│   └── queue_zones.jsonl
|   
│
├── docs/
│   ├── DESIGN.md
│   └── CHOICES.md
│
├── videos/
│
├── dashboard.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md

---

# Quick Setup (5 Commands)

## 1. Clone Repository

```bash
git clone <repository-url>
cd store-intelligence

## 2. Install Dependencies
Install Dependencies

## 3. Run Detection Pipeline
python pipeline/run_entry.py
python pipeline/run_zone.py
python pipeline/run_billing.py

## 4. Start Analytics API
Start Analytics API

APi: http://localhost:8000

Swagger Documentation: http://localhost:8000/docs

## 5. Launch Dashboard
streamlit run dashboard.py

Dashboard: http://localhost:8501

# Event Schema
All generated events follow a unified JSON schema.

{
  "event_id": "uuid",
  "store_id": "STORE_001",
  "camera_id": "CAM1S1",
  "visitor_id": "VIS_12",
  "event_type": "ZONE_ENTER",
  "timestamp": "2026-06-04T15:00:00Z",
  "zone_id": "SKINCARE",
  "dwell_ms": 5000,
  "is_staff": false,
  "confidence": 0.91,
  "metadata": {
    "queue_depth": null,
    "sku_zone": "SKINCARE",
    "session_seq": 3
  }
}

Supported Events

Entry Events
        STORE_ENTER
        STORE_EXIT
Zone Events
        ZONE_ENTER
        ZONE_EXIT
Billing Events
        QUEUE_ENTER
PURCHASE
        QUEUE_UPDATE


# Staff Exclusion

Store staff are excluded from analytics using appearance-based uniform detection.

Implemented for:

STORE_002

Staff traffic is filtered from visitor metrics and business analytics.


# Visitor Re-Identification

The system maintains a global visitor identity across cameras.

Approach:

Appearance feature extraction
Similarity matching
Global visitor IDs

Example:

CAM1 Track 4
→ VIS_12

CAM2 Track 18
→ VIS_12

This prevents double-counting when the same visitor appears across multiple cameras.

# API Endpoints
Metrics

GET /metrics/{store_id}

Returns:

Unique visitors
Conversion rate
Abandonment rate
Average dwell time
Queue depth

# Funnel

GET /funnel/{store_id}

Returns:

Store visitors
Zone visitors
Queue visitors
Purchases

# Heatmap

GET /heatmap/{store_id}

Returns zone-wise visitor distribution.

# Anomalies

GET /anomalies/{store_id}

Returns detected business anomalies including:

Conversion drops
Dead zones
Queue spikes

# Dashboard

The Streamlit dashboard provides:

Live visitor metrics
Conversion analytics
Funnel visualization
Zone heatmap
Queue monitoring
Anomaly alerts

The dashboard consumes data directly from the FastAPI analytics service.

# Technology Stack
Python 3.12
YOLOv8s
ByteTrack
OpenCV
FastAPI
Streamlit
Docker

Notes
Frame skipping is used for faster processing.
Staff traffic is excluded from analytics.
Cross-camera ReID reduces visitor double-counting.
Dockerized deployment is provided for reproducible execution.
Event logs are generated in JSONL format as required by the challenge.