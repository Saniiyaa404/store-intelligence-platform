 # CHOICES.md

# Engineering Choices

This document explains major design decisions made during implementation.

---

# Choice 1: Detection Model

## Options Considered

1. YOLOv8n
2. YOLOv8s
3. Larger YOLO variants

---

## AI Suggestion

Use YOLOv8s because it provides a strong balance between speed and detection quality.

---

## Final Choice

YOLOv8s

---

## Reason

YOLOv8n was faster but produced lower detection quality in crowded retail scenes.

Larger models improved accuracy slightly but increased processing time significantly.

YOLOv8s provided the best balance between:

- Accuracy
- Runtime performance
- Ease of deployment

for the available hardware.

---

# Choice 2: Event Schema

## Options Considered

1. Separate schema per event type
2. Unified schema for all events

---

## AI Suggestion

Use a unified event schema.

---

## Final Choice

Unified event schema.

---

## Reason

A common schema simplifies:

- Storage
- Filtering
- Analytics
- Dashboard integration

All event types share common attributes such as:

- visitor_id
- timestamp
- camera_id
- store_id
- confidence

making a unified structure more maintainable.

---

# Choice 3: API Architecture

## Options Considered

1. Direct file processing inside dashboard
2. REST API architecture

---

## AI Suggestion

Expose analytics through FastAPI.

---

## Final Choice

FastAPI-based analytics service.

---

## Reason

FastAPI provides:

- Clean separation of concerns
- Reusable analytics endpoints
- Easy dashboard integration
- Docker deployment support

This architecture more closely resembles a production system.

---

# Choice 4: Re-Identification Strategy

## Options Considered

1. No ReID
2. Deep-learning ReID model
3. Lightweight appearance matching

---

## AI Suggestion

Use lightweight appearance matching.

---

## Final Choice

Appearance-assisted ReID.

---

## Reason

A full deep-learning ReID solution would require additional training, model downloads and integration effort.

Appearance matching using color histograms provided a practical compromise and enabled cross-camera visitor identity tracking within the hackathon timeframe.

---

# Choice 5: Staff Detection

## Options Considered

1. Count everyone
2. Train staff classifier
3. Uniform-based detection

---

## AI Suggestion

Use uniform-based staff detection.

---

## Final Choice

Uniform-based detection.

---

## Reason

No labeled staff dataset was available.

Store staff wore visually distinct uniforms, making appearance-based detection sufficient for excluding staff from analytics.

---

# VLM Usage

No Vision Language Model (VLM) was used in the production pipeline.

Visual processing was performed using:

- YOLOv8s for person detection
- ByteTrack for tracking
- Polygon-based zone classification
- Appearance-based ReID
- Uniform-based staff exclusion

This approach provided deterministic behavior and lower runtime overhead.