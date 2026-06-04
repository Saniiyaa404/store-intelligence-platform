import supervision as sv


def create_tracker():

    return sv.ByteTrack(
        track_activation_threshold=0.20,
        lost_track_buffer=90,
        minimum_matching_threshold=0.75,
        frame_rate=30,
        minimum_consecutive_frames=3
    )


def track(tracker, detections):

    return tracker.update_with_detections(
        detections
    )