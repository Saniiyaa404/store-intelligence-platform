import cv2
import numpy as np
from datetime import datetime


GLOBAL_VISITOR_COUNTER = 1

TRACK_TO_GLOBAL = {}

RECENT_EXITS = []

LAST_SEEN = {}

def get_histogram(crop):

    if crop.size == 0:
        return None

    hsv = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2HSV
    )

    hist = cv2.calcHist(
        [hsv],
        [0, 1],
        None,
        [16, 16],
        [0, 180, 0, 256]
    )

    cv2.normalize(
        hist,
        hist
    )

    return hist.flatten()


def appearance_similarity(
    hist1,
    hist2
):

    if hist1 is None:
        return 0

    if hist2 is None:
        return 0

    return cv2.compareHist(
        hist1.astype("float32"),
        hist2.astype("float32"),
        cv2.HISTCMP_CORREL
    )


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

    global TRACK_TO_GLOBAL

    key = (
        camera_id,
        track_id
    )

    if key in TRACK_TO_GLOBAL:

        return TRACK_TO_GLOBAL[key]

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

    TRACK_TO_GLOBAL[
        key
    ] = visitor_id

    return visitor_id

def update_track_state(
    camera_id,
    track_id,
    crop,
    timestamp
):

    key = (
        camera_id,
        track_id
    )

    LAST_SEEN[key] = {

        "timestamp":
        timestamp,

        "hist":
        get_histogram(
            crop
        )
    }


def register_track_exit(
    camera_id,
    track_id
):

    key = (
        camera_id,
        track_id
    )

    if key not in LAST_SEEN:
        return

    if key not in TRACK_TO_GLOBAL:
        return
    
    print(
        f"EXIT SAVED "
        f"{TRACK_TO_GLOBAL[key]}"
    )

    RECENT_EXITS.append({

        "visitor_id":
        TRACK_TO_GLOBAL[key],

        "camera_id":
        camera_id,

        "timestamp":
        LAST_SEEN[key]["timestamp"],

        "hist":
        LAST_SEEN[key]["hist"]
    })

    if len(RECENT_EXITS) > 100:

        RECENT_EXITS.pop(0)