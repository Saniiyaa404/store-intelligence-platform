from app.ingestion import get_events
from app.constants import ALL_ZONES
from datetime import datetime
from datetime import timezone
from datetime import timedelta

HISTORICAL_CONVERSIONS = [
    0.40,
    0.35,
    0.45,
    0.50,
    0.38,
    0.42,
    0.44
]

def detect_anomalies(store_id):

    events = get_events()

    store_events = [
        e for e in events
        if e["store_id"] == store_id
        and e["is_staff"] is False
    ]

    store_visitors = set()
    purchase_visitors = set()

    anomalies = []

    max_queue_depth = 0

    #queue spike
    for event in store_events:

        if event["event_type"] != "QUEUE_UPDATE":
            continue

        depth = event["metadata"].get(
            "queue_depth",
            0
        )

        max_queue_depth = max(
            max_queue_depth,
            depth
        )

    #Conversion drop
    for event in store_events:

        visitor_id = event["visitor_id"]

        if visitor_id is None:
            continue

        if event["event_type"] == "STORE_ENTER":

            store_visitors.add(
                visitor_id
            )

        elif event["event_type"] == "PURCHASE":

            purchase_visitors.add(
                visitor_id
            )

    severity = None

    if max_queue_depth >= 10:

        severity = "CRITICAL"

    elif max_queue_depth >= 5:

        severity = "WARN"

    elif max_queue_depth >= 3:

        severity = "INFO"


    if severity is not None:

        anomalies.append({

            "type":
            "BILLING_QUEUE_SPIKE",

            "severity":
            severity,

            "message":
            f"Queue depth reached {max_queue_depth}",

            "suggested_action":
            "Open additional billing counter"
        })

    #conversion vs 7 day avg
    visitor_count = len(
        store_visitors
    )

    purchase_count = len(
        purchase_visitors
    )

    if visitor_count == 0:

        current_conversion = 0

    else:

        current_conversion = (
            purchase_count
            /
            visitor_count
        )

    avg_conversion = (

        sum(
            HISTORICAL_CONVERSIONS
        )

        /

        len(
            HISTORICAL_CONVERSIONS
        )

    )

    if current_conversion < (

        avg_conversion * 0.5

    ):

        anomalies.append({

            "type":
            "CONVERSION_DROP",

            "severity":
            "CRITICAL",

            "message":
            (
                f"Conversion dropped to "
                f"{current_conversion:.2f} "
                f"vs 7-day avg "
                f"{avg_conversion:.2f}"
            ),

            "suggested_action":
            (
                "Review staffing, "
                "promotions and checkout"
            )

        })

    #dead zone code   
    zone_visits = {}
    last_zone_visit = {}

    for event in store_events:

        if event["event_type"] == "ZONE_ENTER":

            zone = event["zone_id"]

            if zone is None:
                continue

            zone_visits[zone] = (
                zone_visits.get(zone, 0)
                + 1
            )

            event_time = datetime.fromisoformat(
                event["timestamp"].replace(
                    "Z",
                    "+00:00"
                )
            )

            if (
                zone not in last_zone_visit
                or
                event_time >
                last_zone_visit[zone]
            ):

                last_zone_visit[zone] = event_time

    now = datetime.now(
        timezone.utc
    )

    for zone in ALL_ZONES:

        last_seen = last_zone_visit.get(
            zone
        ) 

        if last_seen is None:

            anomalies.append({

                "type":
                "DEAD_ZONE",

                "severity":
                "WARN",

                "message":
                f"No visits ever detected in {zone}",

                "suggested_action":
                "Review product placement and merchandising"
            })

        elif (
            now - last_seen
        ) > timedelta(minutes=30):

            anomalies.append({

                "type":
                "DEAD_ZONE",

                "severity":
                "WARN",

                "message":
                f"No visits in {zone} for 30+ minutes",

                "suggested_action":
                "Review product placement and merchandising"
            })

        

    return {
        "store_id": store_id,
        "anomalies": anomalies
    }