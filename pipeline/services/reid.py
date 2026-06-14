import cv2
import numpy as np
from datetime import datetime

from services.reid_engine import (
    get_histogram,
    appearance_similarity
)

from services.identity_manager import (
    identity_manager
)

GLOBAL_VISITOR_COUNTER = 1

RECENT_EXITS = []

def create_global_id():

    global GLOBAL_VISITOR_COUNTER

    visitor_id = (
        f"VIS_"
        f"{GLOBAL_VISITOR_COUNTER}"
    )

    GLOBAL_VISITOR_COUNTER += 1

    return visitor_id


def get_global_visitor_id(
    camera_id,
    track_id,
    crop,
    timestamp
):


    visitor_id = (
        identity_manager.get_visitor_for_track(
            camera_id,
            track_id
        )
    )

    if visitor_id is not None:

        return visitor_id

    hist = get_histogram(
        crop
    )

    best_match = None

    best_score = 0

    for candidate in RECENT_EXITS:

        if candidate["camera_id"] == camera_id:
            continue

        gap = (
            timestamp -
            candidate["timestamp"]
        ).total_seconds()

        if gap > 15:
            continue

        score = appearance_similarity(
            hist,
            candidate["hist"]
        )

        if score > best_score:

            best_score = score

            best_match = candidate

    print(
        f"BEST SCORE={best_score:.3f}"
    )

    if (
        best_match is not None
        and
        best_score > 0.8
    ):

        print(
            f"REID MATCH -> "
            f"{best_match['visitor_id']} "
            f"SCORE={best_score:.3f}"
        )

        visitor_id = (
            best_match[
                "visitor_id"
            ]
        )

    else:

        print(
            f"NEW VISITOR "
            f"SCORE={best_score:.3f}"
        )

        visitor_id = (
            create_global_id()
        )

    identity_manager.assign_track(
        camera_id,
        track_id,
        visitor_id
    )

    return visitor_id

def update_track_state(
    camera_id,
    track_id,
    crop,
    timestamp
):

    visitor_id = (
        identity_manager.get_visitor_for_track(
            camera_id,
            track_id
        )
    )

    if visitor_id is None:
        return
    
    hist = get_histogram(
        crop
    )

    identity_manager.update_active_visitor(
        visitor_id,
        hist,
        timestamp
    )


def register_track_exit(
    camera_id,
    track_id
):

    key = (
        camera_id,
        track_id
    )

    visitor_id = (
        identity_manager.get_visitor_for_track(
            camera_id,
            track_id
        )
    )

    if visitor_id is None:
        return
    
    visitor_data = (
        identity_manager.get_visitor_data(
            visitor_id
        )
    )

    if visitor_data is None:
        return
    
    print(visitor_data)
    
    print(
        f"EXIT SAVED "
        f"{visitor_id}"
    )

    RECENT_EXITS.append({

        "visitor_id":
        visitor_id,

        "camera_id":
        camera_id,

        "timestamp":
        visitor_data["last_seen"],

        "hist":
        visitor_data["embedding"]
    })

    if len(RECENT_EXITS) > 100:

        RECENT_EXITS.pop(0)