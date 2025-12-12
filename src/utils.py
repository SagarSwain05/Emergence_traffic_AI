# utils.py
import threading
import time

class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        # 4-lane camera system
        self.camera_frames = {
            "N": None,  # North
            "E": None,  # East
            "S": None,  # South
            "W": None   # West
        }
        self.detections = {
            "N": [],  # detections per lane
            "E": [],
            "S": [],
            "W": []
        }
        self.ambulance_detected = {
            "N": False,  # ambulance per lane
            "E": False,
            "S": False,
            "W": False
        }
        # priority/control
        self.priority_mode = False
        self.priority_lane = None  # which lane has ambulance (N/E/S/W)
        self.last_emergency_time = 0.0
        self.siren_detected = False
        # Parameters for vehicle simulation (can be updated at runtime via dashboard)
        # spawn_interval: tuple(min_seconds, max_seconds)
        # speed_multiplier: float applied to spawned vehicle speeds
        self.vehicle_params = {
            "spawn_interval": (2.0, 5.0),
            "speed_multiplier": 1.0
        }

shared_state = SharedState()
