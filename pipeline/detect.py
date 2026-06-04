from ultralytics import YOLO

model = YOLO("yolov8s.pt")

def detect(frame):

    results = model(
        frame,
        classes=[0],
        verbose=False
    )

    return results[0]