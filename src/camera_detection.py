# camera_detection.py
import cv2
from ultralytics import YOLO
import threading
import time
from utils import shared_state

# Load YOLO (will auto-download yolov8n.pt)
model = YOLO("yolov8n.pt")

# Adjust this set to match YOLO class names that correspond to emergency vehicles.
EMERGENCY_CLASSES = set(["ambulance", "fire truck", "police car", "fireengine", "fire_engine", "ambulance"]) 

def map_x_y_to_lane(x, y, w, h, frame_w, frame_h):
    cx = x + w/2
    cy = y + h/2
    # divide into 3x3 grid roughly; map center zones to lanes
    # top zone = North, bottom = South, left = West, right = East.
    if cy < frame_h * 0.35:
        return "N"
    if cy > frame_h * 0.65:
        return "S"
    if cx < frame_w * 0.35:
        return "W"
    if cx > frame_w * 0.65:
        return "E"
    # else default to nearest axis
    if abs(cx - frame_w/2) > abs(cy - frame_h/2):
        return "E" if cx > frame_w/2 else "W"
    else:
        return "S" if cy > frame_h/2 else "N"

def camera_loop(camera_index=0, conf_thresh=0.35):
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW if hasattr(cv2, 'CAP_DSHOW') else 0)
    if not cap.isOpened():
        print("ERROR: Could not open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        # store frame for UI
        with shared_state.lock:
            shared_state.camera_frame = frame.copy()

        # Run YOLO on frame (resize to speed up)
        small = cv2.resize(frame, (640, int(frame.shape[0] * 640 / frame.shape[1])))
        results = model(small, conf=conf_thresh, verbose=False)

        # default no detection
        detected = False
        lane = None
        detections = []  # collect all boxes for visualization

        # The results list contains one 'result' object
        for res in results:
            boxes = res.boxes
            if boxes is None or len(boxes) == 0:
                continue
            for box in boxes:
                cls_id = int(box.cls[0])
                name = res.names.get(cls_id, "").lower()
                # get bounding box coords (on small frame)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                w = x2 - x1
                h = y2 - y1
                # map back to original frame scale
                scale_x = frame.shape[1] / small.shape[1]
                scale_y = frame.shape[0] / small.shape[0]
                rx1 = x1 * scale_x
                ry1 = y1 * scale_y
                rx2 = x2 * scale_x
                ry2 = y2 * scale_y
                rw = w * scale_x
                rh = h * scale_y
                
                # store all detections for UI overlay
                detections.append({
                    "x1": int(rx1),
                    "y1": int(ry1),
                    "x2": int(rx2),
                    "y2": int(ry2),
                    "label": name,
                    "conf": conf,
                    "is_emergency": any(k in name for k in ["ambulance", "fire", "police"])
                })
                
                # check label for emergency keywords
                if any(k in name for k in ["ambulance", "fire", "police"]):
                    lane = map_x_y_to_lane(rx1, ry1, rw, rh, frame.shape[1], frame.shape[0])
                    detected = True

        with shared_state.lock:
            shared_state.ambulance_detected = detected
            shared_state.ambulance_lane = lane if detected else None
            shared_state.detections = detections
            if detected:
                shared_state.last_emergency_time = time.time()

    cap.release()

def start_camera_thread(camera_index=0):
    t = threading.Thread(target=camera_loop, args=(camera_index,), daemon=True)
    t.start()
    return t

if __name__ == "__main__":
    start_camera_thread()
    import time
    while True:
        with shared_state.lock:
            print("Detected:", shared_state.ambulance_detected, shared_state.ambulance_lane)
        time.sleep(1)
