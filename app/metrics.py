from app.ingestion import get_events


def calculate_metrics(store_id):

    events = get_events()

    store_events = [
        e for e in events
        if e["store_id"] == store_id
        and e["is_staff"] is False
    ]

    # UNIQUE VISITORS

    unique_visitors = set()

    for event in store_events:

        if event["visitor_id"] is not None:

            unique_visitors.add(
                event["visitor_id"]
            )

    unique_visitors_count = len(
        unique_visitors
    )

    # PURCHASED VISITORS

    purchased_visitors = set()

    for event in store_events:

        if event["event_type"] == "PURCHASE":

            purchased_visitors.add(
                event["visitor_id"]
            )

    purchased_count = len(
        purchased_visitors
    )

    # CONVERSION RATE

    if unique_visitors_count == 0:

        conversion_rate = 0

    else:

        conversion_rate = round(
            purchased_count /
            unique_visitors_count,
            2
        )

    # ABANDONMENT RATE

    if unique_visitors_count == 0:

        abandonment_rate = 0

    else:

        abandonment_rate = round(
            (
                unique_visitors_count -
                purchased_count
            ) /
            unique_visitors_count,
            2
        )

    # AVG DWELL

    dwell_values = []

    for event in store_events:

        if (
            event["event_type"] == "ZONE_EXIT"
            and event["dwell_ms"] > 0
        ):

            dwell_values.append(
                event["dwell_ms"]
            )

    if len(dwell_values) == 0:

        avg_dwell_seconds = 0

    else:

        avg_dwell_seconds = round(
            (
                sum(dwell_values)
                /
                len(dwell_values)
            ) / 1000,
            2
        )

    # AVG DWELL PER ZONE

    zone_dwell = {}

    for event in store_events:

        if (
            event["event_type"] == "ZONE_EXIT"
            and event["dwell_ms"] > 0
        ):

            zone = event["zone_id"]

            if zone not in zone_dwell:

                zone_dwell[zone] = []

            zone_dwell[zone].append(
                event["dwell_ms"]
            )

    avg_dwell_per_zone = {}

    for zone, values in zone_dwell.items():

        avg_dwell_per_zone[zone] = round(
            (
                sum(values)
                /
                len(values)
            ) / 1000,
            2
        )

    # LATEST QUEUE DEPTH

    queue_depth = 0

    queue_events = [

        e for e in store_events

        if e["event_type"] ==
        "QUEUE_UPDATE"
    ]

    if len(queue_events) > 0:

        latest = queue_events[-1]

        queue_depth = latest[
            "metadata"
        ].get(
            "queue_depth",
            0
        )

    return {

        "store_id": store_id,

        "unique_visitors":
        unique_visitors_count,

        "conversion_rate":
        conversion_rate,

        "abandonment_rate":
        abandonment_rate,

        "avg_dwell_seconds":
        avg_dwell_seconds,

        "avg_dwell_per_zone":
        avg_dwell_per_zone,

        "queue_depth":
        queue_depth
    }