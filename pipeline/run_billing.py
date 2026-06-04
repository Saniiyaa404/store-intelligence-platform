import cv2
import supervision as sv

from config import CAMERA_CONFIG
from events import create_event, save_event
from queue_zones import QUEUE_ZONES

from detect import detect
from tracker import create_tracker
from tracker import track

from reid import (
    get_global_visitor_id,
    update_track_state
)
from datetime import datetime
from datetime import timezone
from staff import is_staff

def get_queue_type(camera_id, x, y):

    zones = QUEUE_ZONES.get(
        camera_id,
        {}
    )

    for zone_name, polygon in zones.items():

        if cv2.pointPolygonTest(
            polygon,
            (int(x), int(y)),
            False
        ) >= 0:

            return zone_name

    return None


def run_billing_camera(camera_key):

    print(
        f"Starting {camera_key}"
    )

    tracker_obj = create_tracker()

    camera_config = CAMERA_CONFIG[camera_key]

    CAMERA_ID = camera_config["camera_id"]

    cap = cv2.VideoCapture(
        camera_config["video"]
    )

    last_queue_depth = -1

    queue_entry_frame = {}
    purchase_done = set()
    queue_entered = set()
    staff_tracks = {}

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps == 0:
        fps = 30

    frame_count = 0

    while True:

        frame_count += 1

        success, frame = cap.read()

        if not success:
            break

        if frame_count % 3 != 0:
            continue

        result = detect(frame)

        detections = sv.Detections.from_ultralytics(
            result
        )

        tracked = track(tracker_obj, detections)

        queue_depth = 0      # <-- YAHAN

        if len(tracked) > 0:

            for i, box in enumerate(tracked.xyxy):

                if tracked.tracker_id is None:
                    continue

                track_id = tracked.tracker_id[i]

                x1, y1, x2, y2 = box

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
                        f"ID={track_id}"
                    )

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

                cv2.rectangle(
                    frame,
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    (0,255,0),
                    2
                )

                center_x = int((x1+x2)/2)
                center_y = int((y1+y2)/2)

                cv2.circle(
                    frame,
                    (center_x, center_y),
                    5, #radius
                    (0, 255, 255), #yellow color
                    -1 #filled circle
                )

                location = get_queue_type(
                    CAMERA_ID,
                    # foot_x, foot_y
                    center_x, center_y
                )

                print(
                    f"TRACK={track_id} "
                    f"LOC={location}"
                )

                if location == "STAFF" or staff_flag:
                    continue

                if location == "QUEUE":

                    queue_depth += 1

                    if track_id not in queue_entered:

                        event = create_event(
                            visitor_id=global_visitor_id,
                            event_type="QUEUE_ENTER",
                            zone_id="BILLING",
                            dwell_ms=0,
                            session_seq=1,
                            camera_id=camera_config["camera_id"],
                            store_id=camera_config["store_id"],
                            is_staff=staff_flag,
                            confidence=float(
                                tracked.confidence[i]
                            )
                        )

                        event["metadata"]["queue_depth"] = queue_depth

                        save_event(event)

                        queue_entered.add(track_id)

                        print(
                            f"QUEUE_ENTER VISITOR={track_id}"
                        )

                    if track_id is not None:

                        if track_id not in queue_entry_frame:

                            queue_entry_frame[track_id] = frame_count

                        time_in_queue = (
                            frame_count -
                            queue_entry_frame[track_id]
                        ) / fps

                        if (
                            time_in_queue >= 2
                            and track_id not in purchase_done
                        ):

                            print(
                                f"PURCHASE VISITOR={track_id}"
                            )

                            event = create_event(
                                visitor_id=global_visitor_id,
                                event_type="PURCHASE",
                                zone_id="BILLING",
                                dwell_ms=int(
                                    time_in_queue * 1000
                                ),
                                session_seq=1,
                                camera_id=camera_config["camera_id"],
                                store_id=camera_config["store_id"],
                                is_staff=staff_flag,
                                confidence=float(
                                    tracked.confidence[i]
                                )
                            )

                            event["metadata"]["queue_depth"] = queue_depth

                            save_event(event)

                            purchase_done.add(track_id)

                else:

                    if tracked.tracker_id is not None:

                        track_id = tracked.tracker_id[i]

                        if track_id in queue_entry_frame:

                            del queue_entry_frame[track_id]

                
                cv2.putText(
                        frame,
                        str(track_id),
                        (center_x, center_y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0,255,0),
                        2
                    )

        # <-- FOR LOOP KHATAM

        cv2.putText(
            frame,
            f"QUEUE={queue_depth}",
            (50,50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

        # <-- YAHAN EVENT EMIT HOGA

        if queue_depth != last_queue_depth:
            
            #debug
            print(
                f"QUEUE_DEPTH={queue_depth}"
            )

            event = create_event(
                visitor_id=None,
                event_type="QUEUE_UPDATE",
                zone_id="BILLING",
                dwell_ms=0,
                session_seq=1,
                camera_id=camera_config["camera_id"],
                store_id=camera_config["store_id"],
                is_staff=False
            )

            event["metadata"]["queue_depth"] = queue_depth

            save_event(event)

            last_queue_depth = queue_depth

        #debug
        from queue_zones import QUEUE_ZONES

        for polygon in QUEUE_ZONES[CAMERA_ID].values():

            cv2.polylines(
                frame,
                [polygon],
                True,
                (255,0,0),
                2
            )
        
        cv2.imshow("Billing", frame)
    
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    run_billing_camera(
        "STORE2_CAM5"
    )

