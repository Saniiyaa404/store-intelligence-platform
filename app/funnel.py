from app.ingestion import get_events


def calculate_funnel(store_id):

    events = get_events()

    store_events = [
        e for e in events
        if e["store_id"] == store_id
        and e["is_staff"] is False
    ]

    store_visitors = set()
    zone_visitors = set()
    queue_visitors = set()
    purchase_visitors = set()

    for event in store_events:

        visitor_id = event["visitor_id"]

        if visitor_id is None:
            continue

        if event["event_type"] == "STORE_ENTER":

            store_visitors.add(
                visitor_id
            )

        elif event["event_type"] == "ZONE_ENTER":

            zone_visitors.add(
                visitor_id
            )

        elif event["event_type"] == "QUEUE_ENTER":

            queue_visitors.add(
                visitor_id
            )

        elif event["event_type"] == "PURCHASE":

            purchase_visitors.add(
                visitor_id
            )

    store_count = len(
        store_visitors
    )

    zone_count = len(
        zone_visitors
    )

    queue_count = len(
        queue_visitors
    )

    purchase_count = len(
        purchase_visitors
    )

    if store_count == 0:

        entry_to_zone_dropoff = 0

    else:

        entry_to_zone_dropoff = round(
            (
                store_count -
                zone_count
            )
            /
            store_count
            * 100,
            2
        )

    if zone_count == 0:

        zone_to_queue_dropoff = 0

    else:

        zone_to_queue_dropoff = round(
            (
                zone_count -
                queue_count
            )
            /
            zone_count
            * 100,
            2
        )

    if queue_count == 0:

        queue_to_purchase_dropoff = 0

    else:

        queue_to_purchase_dropoff = round(
            (
                queue_count -
                purchase_count
            )
            /
            queue_count
            * 100,
            2
        )

    return {

        "store_id": store_id,

        "store_visitors":
        store_count,

        "zone_visitors":
        zone_count,

        "queue_visitors":
        queue_count,

        "purchases":
        purchase_count,

        "entry_to_zone_dropoff":
        entry_to_zone_dropoff,

        "zone_to_queue_dropoff":
        zone_to_queue_dropoff,

        "queue_to_purchase_dropoff":
        queue_to_purchase_dropoff
    }