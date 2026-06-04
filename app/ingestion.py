import json

from app.database import conn
from app.database import cursor

#duplicate detection using -> event_id PRIMARY KEY

def ingest_events(events):

    inserted = 0
    duplicates = 0

    for event in events:

        try:

            cursor.execute(

                """
                INSERT INTO events (

                    event_id,
                    store_id,
                    camera_id,
                    visitor_id,

                    event_type,
                    timestamp,

                    zone_id,

                    dwell_ms,

                    is_staff,

                    confidence,

                    metadata

                )

                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,

                (

                    event.event_id,

                    event.store_id,
                    event.camera_id,

                    event.visitor_id,

                    event.event_type,
                    event.timestamp,

                    event.zone_id,

                    event.dwell_ms,

                    int(event.is_staff),

                    event.confidence,

                    json.dumps(
                        event.metadata
                    )

                )

            )

            inserted += 1

        except Exception:

            duplicates += 1

    conn.commit()

    return {

        "inserted":
        inserted,

        "duplicates":
        duplicates
    }


def get_events():

    cursor.execute(
        "SELECT * FROM events"
    )

    rows = cursor.fetchall()

    events = []

    for row in rows:

        events.append({

            "event_id":
            row[0],

            "store_id":
            row[1],

            "camera_id":
            row[2],

            "visitor_id":
            row[3],

            "event_type":
            row[4],

            "timestamp":
            row[5],

            "zone_id":
            row[6],

            "dwell_ms":
            row[7],

            "is_staff":
            bool(row[8]),

            "confidence":
            row[9],

            "metadata":
            json.loads(row[10])

        })

    return events

#testing
def clear_events():

    cursor.execute(
        "DELETE FROM events"
    )

    conn.commit()