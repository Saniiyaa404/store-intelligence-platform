import cv2
import supervision as sv

from config import CAMERA_CONFIG
from services.events import create_event, save_event
from zones import get_zone, CAMERA_ZONES

from services.detect import detect
from services.tracker import create_tracker
from services.tracker import track

from services.reid import (
    get_global_visitor_id,
    update_track_state,
    register_track_exit
)
from datetime import datetime, timezone

from staff import is_staff

def run_zone_camera(camera_key):

    print(
        f"Starting {camera_key}"
    )

    tracker_obj = create_tracker()

    camera_config = CAMERA_CONFIG[camera_key]

    CAMERA_ID = camera_config["camera_id"]

    cap = cv2.VideoCapture(
        camera_config["video"]
    )

    fps = cap.get(cv2.CAP_PROP_FPS)

    confirmation_frames = camera_config[
        "confirmation_frames"
    ]

    from processors.zone_processor import ZoneProcessor
    processor = ZoneProcessor(
        confirmation_frames
    )

    staff_tracks = {}

    previous_track_ids = set()

    frame_number = 0

    while True:
        frame_number += 1
        print(CAMERA_ID)

        success, frame = cap.read()

        if not success:
            break

        if frame_number % 3 != 0:
            continue

        result = detect(frame)

        detections = sv.Detections.from_ultralytics(
            result
        )

        tracked = track(tracker_obj, detections)
        #tracked -> xyxy, confidence, class_id, tracker_id

        current_track_ids = set()

        if len(tracked) > 0: #if person detected

            for i, box in enumerate(tracked.xyxy):

                x1, y1, x2, y2 = box

                #create bounding box
                cv2.rectangle(
                    frame,
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    (0, 255, 0),
                    2
                )

                #find center coordinates for the detected person
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                foot_x = int((x1+x2)/2)
                foot_y = int(y2)

                head_x = int((x1+x2)/2)
                head_y = int(y1 + (y2-y1)*0.25)

                #draw yellow dot
                # cv2.circle(
                #     frame,
                #     (center_x, center_y),
                #     5, #radius
                #     (0, 255, 255), #yellow color
                #     -1 #filled circle
                # )

                # cv2.circle(
                #     frame,
                #     (foot_x, foot_y),
                #     5, #radius
                #     (0, 0, 255), #orange color
                #     -1 #filled circle
                # )

                # cv2.circle(
                #     frame,
                #     (head_x, head_y),
                #     5, #radius
                #     (255, 255, 0),
                #     -1 #filled circle
                # )

            

                #if tracker_id of that particular detection exists ->
                if tracked.tracker_id is not None:

                    track_id = tracked.tracker_id[i]

                    crop = frame[
                        int(y1):int(y2),
                        int(x1):int(x2)
                    ]

                    if track_id not in staff_tracks:

                        staff_tracks[track_id] = is_staff(
                            crop,
                            camera_config["store_id"]
                        )

                    staff_flag = staff_tracks[track_id]

                    if staff_flag:

                        print(
                            f"STAFF DETECTED "
                             f"STORE={camera_config['store_id']} "
                            f"ID={track_id}"
                        )

                    current_track_ids.add(track_id)

                    crop = frame[
                        int(y1):int(y2),
                        int(x1):int(x2)
                    ]

                    timestamp = datetime.now(
                        timezone.utc
                    )

                    global_visitor_id = (
                        get_global_visitor_id(
                            camera_id=CAMERA_ID,
                            track_id=track_id,
                            crop=crop,
                            timestamp=timestamp
                        )
                    )

                    update_track_state(
                        camera_id=CAMERA_ID,
                        track_id=track_id,
                        crop=crop,
                        timestamp=timestamp
                    )

                    print(
                        f"LOCAL={track_id} "
                        f"GLOBAL={global_visitor_id}"
                    )

                    zone = get_zone(
                        CAMERA_ID,
                        head_x,
                        head_y
                    )

                    previous_zone = (
                        processor.get_current_zone(
                            track_id
                        )
                    )

                    processor.update_zone_candidate(
                        track_id,
                        zone
                    )

                    print(
                        f"ID={track_id} "
                        f"CAND={processor.zone_candidate.get(track_id)} "
                        f"COUNT={processor.zone_candidate_count.get(track_id,0)}"
                    )

                    # if track_id not in entry_frame:
                    #     entry_frame[track_id] = frame_number

                    print(
                        f"ID={track_id} "
                        f"PREV={previous_zone} "
                        f"CAND={zone}"
                    )

                    if (
                        processor.is_pending_exit(track_id)
                        and zone is not None
                    ):
                        processor.clear_pending_exit(
                            track_id
                        )

                    # ENTER EVENT

                    if previous_zone is None and \
                    zone is not None and \
                    processor.is_zone_confirmed(track_id):

                        print(
                            f"ID={track_id} ENTERED {zone}"
                        )
                        

                        event = create_event(
                            visitor_id=global_visitor_id,
                            event_type="ZONE_ENTER",
                            zone_id=zone,
                            dwell_ms=0,
                            confidence=float(tracked.confidence[i]),
                            session_seq=processor.get_session_seq(
                                track_id
                            ),
                            camera_id=camera_config["camera_id"],
                            store_id=camera_config["store_id"],
                            is_staff=bool(staff_flag)
                        )

                        save_event(event)

                        processor.reset_zone_candidate(
                            track_id
                        )

                        processor.start_zone_visit(
                            track_id,
                            zone,
                            frame_number
                        )

                    # ZONE CHANGE

                    elif previous_zone != zone and \
                        previous_zone is not None and \
                        zone is not None:

                        print(
                            f"ID={track_id} MOVED "
                            f"{previous_zone} -> {zone}"
                        )

                        enter_frame = processor.get_entry_frame(
                            track_id,
                            frame_number
                        )

                        dwell_seconds = (
                            frame_number - enter_frame
                        ) / fps

                        exit_event = create_event(
                            visitor_id=global_visitor_id,
                            event_type="ZONE_EXIT",
                            zone_id=previous_zone,
                            dwell_ms=int(dwell_seconds * 1000),
                            confidence=float(tracked.confidence[i]),
                            session_seq=processor.get_session_seq(track_id),
                            camera_id=camera_config["camera_id"],
                            store_id=camera_config["store_id"],
                            is_staff=staff_flag
                        )

                        save_event(exit_event)

                        processor.increment_session_seq(
                            track_id
                        )

                        enter_event = create_event(
                            visitor_id=global_visitor_id,
                            event_type="ZONE_ENTER",
                            zone_id=zone,
                            dwell_ms=0,
                            confidence=float(tracked.confidence[i]),
                            session_seq=processor.get_session_seq(track_id),
                            camera_id=camera_config["camera_id"],
                            store_id=camera_config["store_id"],
                            is_staff=staff_flag
                        )

                        save_event(enter_event)

                        processor.increment_session_seq(
                            track_id
                        )

                        print(
                            f"ID={track_id} EXITED "
                            f"{previous_zone}"
                        )

                        print(
                            f"DWELL = {dwell_seconds:.2f}"
                        )

                        print(
                            f"ID={track_id} ENTERED {zone}"
                        )

                        processor.start_zone_visit(
                            track_id,
                            zone,
                            frame_number
                        )

                    #EXIT
                    elif previous_zone is not None and zone is None:

                        if not processor.is_pending_exit(
                            track_id
                        ):
                            processor.mark_pending_exit(
                                track_id,
                                frame_number
                            )


                    #draw id on screen near center point
                    # cv2.putText(
                    #     frame,
                    #     str(track_id),
                    #     (center_x, center_y),
                    #     cv2.FONT_HERSHEY_SIMPLEX,
                    #     0.8,
                    #     (0,255,0),
                    #     2
                    # )


        disappeared_tracks = (
            previous_track_ids -
            current_track_ids
        )

        for track_id in disappeared_tracks:

            register_track_exit(
                CAMERA_ID,
                track_id
            )

            print(
                f"TRACK EXITED: {track_id}"
            )

        previous_track_ids = (
            current_track_ids.copy()
        )


        #FINAL EXIT
        for track_id in list(processor.get_pending_exit_tracks()):

            exit_frame = (
                processor.get_pending_exit_frame(
                    track_id
                )
            )

            if frame_number - exit_frame >= 30:

                print(
                    f"ID={track_id} FINAL EXIT"
                )

                zone_name = processor.get_last_zone(
                    track_id
                )

                if zone_name is not None:

                    enter_frame = processor.get_entry_frame(
                        track_id,
                        frame_number
                    )

                    dwell_seconds = (
                        frame_number - enter_frame
                    ) / fps

                    event = create_event(
                        visitor_id=global_visitor_id,
                        event_type="ZONE_EXIT",
                        zone_id=zone_name,
                        dwell_ms=int(dwell_seconds * 1000),
                        session_seq=processor.get_session_seq(track_id),
                        camera_id=camera_config["camera_id"],
                        store_id=camera_config["store_id"],
                        is_staff=staff_flag
                    )

                    save_event(event)

                # print(f"BEFORE DELETE: {pending_exit.keys()}")

                processor.clear_pending_exit(
                    track_id
                )

                # print(f"AFTER DELETE: {pending_exit.keys()}") 

                processor.clear_zone_visit(
                    track_id
                )

        from zones import CAMERA_ZONES

        for polygon in CAMERA_ZONES[CAMERA_ID].values():

            cv2.polylines(
            frame,
            [polygon],
            True,
            (255,0,0),
            2
            )


        # show video by opening window
        cv2.imshow("Zone", frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    run_zone_camera(
        "STORE1_CAM2"
    )