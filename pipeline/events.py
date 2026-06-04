import uuid
import json
from datetime import datetime, timezone
import threading

file_lock = threading.Lock()


def create_event(
    visitor_id,
    event_type,
    zone_id,
    dwell_ms,
    session_seq,
    camera_id,
    store_id,
    confidence=1.0,
    is_staff=False
):

    event = {
        "event_id": str(uuid.uuid4()),
        "store_id": store_id,
        "camera_id": camera_id,
        "visitor_id": None if visitor_id is None else str(visitor_id),
        "event_type": event_type,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "zone_id": zone_id,
        "dwell_ms": dwell_ms,
        "is_staff": is_staff,
        "confidence": confidence,
        "metadata": {
            "queue_depth": None,
            "sku_zone": zone_id,
            "session_seq": session_seq
        }
    }

    return event


def save_event(event):

    with file_lock:

        with open(
            "events.jsonl",
            "a"
        ) as f:

            f.write(
                json.dumps(event)
            )

            f.write("\n")