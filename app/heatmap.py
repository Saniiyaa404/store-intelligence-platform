from app.ingestion import get_events


def calculate_heatmap(store_id):

    events = get_events()
    zone_stats = {}
    zones = []
    unique_visitors = set()

    store_events = [
        e for e in events
        if e["store_id"] == store_id
        and e["is_staff"] is False
    ]

    for event in store_events:

        visitor = event["visitor_id"]

        if visitor is not None:

            unique_visitors.add(
                visitor
            )

        if event["event_type"] != "ZONE_EXIT":
            continue

        zone = event["zone_id"]

        if zone is None:
            continue

        if zone not in zone_stats:

            zone_stats[zone] = {
                "visits": 0,
                "total_dwell": 0
            }

        zone_stats[zone]["visits"] += 1

        zone_stats[zone]["total_dwell"] += (
            event["dwell_ms"]
        )

    data_confidence = (
        len(unique_visitors) >= 20
    )

    for zone_name, stats in zone_stats.items():

        avg_dwell = (
            stats["total_dwell"]
            /
            stats["visits"]
            /
            1000
        )

        engagement_score = (
            stats["visits"]
            *
            avg_dwell
        )

        zones.append({

            "zone": zone_name,

            "visit_count":
            stats["visits"],

            "avg_dwell_seconds":
            round(avg_dwell, 2),

            "raw_score":
            engagement_score

        })

    if len(zones) == 0:

        return {
            "store_id": store_id,
            "data_confidence": data_confidence,
            "zones": []
        }
    
    #using unique visitors as session proxy
    max_score = max(
        z["raw_score"]
        for z in zones
    )

    for zone in zones:

        zone["heat_score"] = round(
            (
                zone["raw_score"]
                /
                max_score
            )
            * 100
        )

        del zone["raw_score"]

    return {

        "store_id": store_id,

        "data_confidence":
        data_confidence,

        "zones":
        zones
    }