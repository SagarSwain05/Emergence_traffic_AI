# traffic_controller.py
import time
from utils import shared_state

# Timing for normal cycle (8 seconds per lane: 6s GREEN + 1s YELLOW + 1s RED)
GREEN_TIME = 6.0      # 6 seconds green per lane in normal mode
YELLOW_TIME = 1.0     # 1 second yellow
RED_TIME = 1.0        # 1 second red (transition time)
CYCLE_TIME = GREEN_TIME + YELLOW_TIME + RED_TIME  # 8 seconds total per lane
POST_PRIORITY_BUFFER = 0.0  # seconds after ambulance before returning to normal (set to 0 to remove delay)

LANES = ["N", "E", "S", "W"]

class TrafficController:
    def __init__(self):
        self.current_lane_idx = 0  # which lane is currently green (0=N, 1=E, 2=S, 3=W)
        self.mode = "NORMAL"  # or "PRIORITY"
        self.lights = {l: "RED" for l in LANES}
        self.lights["N"] = "GREEN"  # Start with North green
        self.last_switch = time.time()
        self.priority_lane = None
        self.priority_start_time = 0

    def set_priority(self, lane):
        """Set traffic to priority mode for a specific lane."""
        if lane not in LANES:
            return
        self.mode = "PRIORITY"
        self.priority_lane = lane
        self.priority_start_time = time.time()
        
        # All red except priority lane
        for l in LANES:
            self.lights[l] = "RED"
        self.lights[lane] = "GREEN"
        self.last_switch = time.time()

    def normal_cycle_step(self):
        """Cycle through lanes N->E->S->W in normal mode with 8s per lane (6G + 1Y + 1R)."""
        now = time.time()
        
        # Check if time to switch to next lane (complete 8s cycle)
        if now - self.last_switch > CYCLE_TIME:
            self.current_lane_idx = (self.current_lane_idx + 1) % len(LANES)
            self.last_switch = now
        
        # Update light states
        for i, lane in enumerate(LANES):
            elapsed = now - self.last_switch
            
            if i == self.current_lane_idx:
                # This lane is currently cycling
                if elapsed <= GREEN_TIME:
                    self.lights[lane] = "GREEN"
                elif elapsed <= GREEN_TIME + YELLOW_TIME:
                    self.lights[lane] = "YELLOW"
                else:
                    self.lights[lane] = "RED"
            else:
                self.lights[lane] = "RED"

    def update(self):
        """Update traffic controller state based on detections."""
        with shared_state.lock:
            # Check if any lane has ambulance
            ambulance_lane = None
            for lane in LANES:
                if shared_state.ambulance_detected[lane]:
                    ambulance_lane = lane
                    break
            
            if ambulance_lane:
                # Priority mode: ambulance detected
                self.set_priority(ambulance_lane)
                shared_state.priority_mode = True
                shared_state.priority_lane = ambulance_lane
            else:
                # No ambulance detected
                if self.mode == "PRIORITY":
                    # Check if enough time has passed since last ambulance
                    if time.time() - shared_state.last_emergency_time > POST_PRIORITY_BUFFER:
                        # Return to normal cycling
                        self.mode = "NORMAL"
                        shared_state.priority_mode = False
                        shared_state.priority_lane = None
                        # Keep current lane green and continue cycle
                
                # Normal cycling
                if self.mode == "NORMAL":
                    self.normal_cycle_step()
        
        return self.lights, self.mode, self.priority_lane

# Global controller instance
controller = TrafficController()
