from app.ingestion import get_events

from datetime import datetime
from datetime import timezone


def get_health():

    events = get_events()

    if len(events) == 0:

        return {
            "status": "NO_DATA",
            "stores": []
        }

    store_latest = {}

    for event in events:

        store_id = event["store_id"]

        event_time = datetime.fromisoformat(
            event["timestamp"]
        )

        if (
            store_id not in store_latest
            or
            event_time >
            store_latest[store_id]
        ):

            store_latest[store_id] = event_time

    stores = []

    now = datetime.now(
        timezone.utc
    )

    for store_id, last_time in store_latest.items():

        lag_minutes = (
            now - last_time
        ).total_seconds() / 60

        stores.append({

            "store_id":
            store_id,

            "last_event_timestamp":
            last_time.isoformat(),

            "lag_minutes":
            round(lag_minutes, 2),

            "stale_feed":
            lag_minutes > 10
        })

    return {

        "status":
        "OK",

        "stores":
        stores
    }