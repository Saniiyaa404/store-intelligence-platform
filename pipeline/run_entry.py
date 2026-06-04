import cv2
import supervision as sv

from detect import detect
from tracker import create_tracker
from tracker import track
from config import CAMERA_CONFIG
from events import create_event, save_event

from reid import (
    get_global_visitor_id,
    update_track_state
)

from datetime import datetime
from datetime import timezone

from staff import is_staff

def run_entry_camera(camera_key):

    print(
        f"Starting {camera_key}"
    )

    tracker_obj = create_tracker()

    camera_config = CAMERA_CONFIG[camera_key]

    CAMERA_ID = camera_config["camera_id"]

    cap = cv2.VideoCapture(
        camera_config["video"]
    )

    entered = set()
    previous_y = {}
    staff_tracks = {}

    ENTRY_LINE_Y = camera_config[
        "entry_line_y"
    ]
    frame_count = 0

    print(cap.isOpened())
    while True:
        
        success, frame = cap.read()
        
        frame_count += 1

        if frame_count % 100 == 0:
            print(frame_count)

        if not success:
            break

        if frame_count % 3 != 0:
            continue

        result = detect(frame)

        detections = sv.Detections.from_ultralytics(
            result
        )

        tracked = track(tracker_obj, detections)
        #tracked -> xyxy, confidence, class_id, tracker_id

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
                cv2.circle(
                    frame,
                    (center_x, center_y),
                    5, #radius
                    (0, 255, 255), #yellow color
                    -1 #filled circle
                )

                cv2.circle(
                    frame,
                    (foot_x, foot_y),
                    5, #radius
                    (0, 0, 255), #orange color
                    -1 #filled circle
                )

                cv2.circle(
                    frame,
                    (head_x, head_y),
                    5, #radius
                    (255, 255, 0),
                    -1 #filled circle
                )

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

                    if track_id not in previous_y:

                        previous_y[track_id] = foot_y

                    old_y = previous_y[track_id]

                    print(
                        f"ID={track_id} "
                        f"OLD={old_y} "
                        f"NEW={foot_y}"
                    )

                    if abs(foot_y - ENTRY_LINE_Y) < 50:

                        print(
                            f"ID={track_id} "
                            f"NEAR LINE "
                            f"Y={foot_y}"
                        )

                    if old_y < ENTRY_LINE_Y and \
                        foot_y > ENTRY_LINE_Y and \
                        track_id not in entered:
                            
                            if staff_flag:
                                continue

                            print(
                                f"ID={track_id} STORE_ENTER"
                            )

                            event = create_event(
                                visitor_id=global_visitor_id,
                                event_type="STORE_ENTER",
                                zone_id=None,
                                dwell_ms=0,
                                session_seq=1,
                                camera_id=camera_config["camera_id"],
                                store_id=camera_config["store_id"],
                                confidence=float(tracked.confidence[i]),
                                is_staff=staff_flag
                            )

                            save_event(event)

                            entered.add(track_id)

                    elif old_y > ENTRY_LINE_Y and \
                        foot_y < ENTRY_LINE_Y and \
                        track_id in entered:

                        if staff_flag:
                            continue

                        print(
                            f"ID={track_id} STORE_EXIT"
                        )

                        event = create_event(
                            visitor_id=global_visitor_id,
                            event_type="STORE_EXIT",
                            zone_id=None,
                            dwell_ms=0,
                            session_seq=1,
                            camera_id=camera_config["camera_id"],
                            store_id=camera_config["store_id"],
                            confidence=float(tracked.confidence[i]),
                            is_staff=staff_flag
                        )

                        save_event(event)

                        entered.remove(track_id)

                    previous_y[track_id] = foot_y

                    cv2.putText(
                        frame,
                        str(track_id),
                        (center_x, center_y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0,255,0),
                        2
                    )
            
        cv2.line(
            frame,
            (0, ENTRY_LINE_Y),
            (frame.shape[1], ENTRY_LINE_Y),
            (0, 0, 255),
            3
        )
            
        #show video by opening window
        # cv2.imshow("Phase 1", frame)

        # if cv2.waitKey(1) == 27:
        #     break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    run_entry_camera(
        "STORE2_ENTRY2"
    )