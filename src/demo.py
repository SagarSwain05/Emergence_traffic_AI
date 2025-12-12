#!/usr/bin/env python3
"""
Demo script for testing the Emergency Traffic AI system without real hardware.

Features:
- Plays video file (or simulated video) showing ambulances
- Plays audio file (or generates test siren) showing detection
- Displays simulated detections to shared_state
- Allows easy testing without a real camera/microphone

Usage:
    python demo.py                          # Use default demo files
    python demo.py --video path/to/video.mp4 --audio path/to/siren.wav
    python demo.py --generate               # Generate synthetic test data

Note: Run main.py in another terminal to see the UI respond to the demo data.
"""

import argparse
import threading
import time
import numpy as np
import cv2
import random
from traffic_controller import controller
from utils import shared_state
from scipy import signal
try:
    import sounddevice as sd
except Exception:
    sd = None

class DemoCamera:
    """Simulates 4-lane camera feeds with ambulances."""
    
    def __init__(self, video_paths=None):
        """
        video_paths: dict with keys "N", "E", "S", "W" for optional video files per lane.
        Otherwise generates synthetic frames.
        """
        self.video_paths = video_paths or {}
        self.running = True
        self.ambulance_lanes = []  # list of lanes currently showing ambulance
        self.ambulance_cycle_time = 0
        self.ambulance_start_time = time.time()  # Track when ambulance started on current lane
        self.current_lane_idx = 0  # Track which lane is active

        # Vehicle simulation state per lane
        self.vehicles = {"N": [], "E": [], "S": [], "W": []}
        # Last spawn timestamp per lane
        self.last_vehicle_spawn = {l: 0 for l in self.vehicles}
        # Vehicle spawn interval range (seconds)
        self.vehicle_spawn_interval = (2.0, 5.0)
        # Speed multiplier applied to spawned vehicle speeds (can be adjusted at runtime)
        self.speed_multiplier = 1.0
    
    def generate_test_frame(self, lane, ambulance_traverse_time=4.0):
        """Generate a synthetic test frame for a specific lane."""
        frame = np.ones((300, 400, 3), dtype=np.uint8) * 100
        
        # Draw background: sky and road
        frame[:150] = (135, 206, 235)  # Sky blue
        frame[150:] = (128, 128, 128)  # Gray road
        
        # Lane-specific road markings and label
        lane_colors = {
            "N": (200, 100, 100),  # Reddish for North
            "E": (100, 200, 100),  # Greenish for East
            "S": (100, 100, 200),  # Blueish for South
            "W": (200, 200, 100)   # Yellowish for West
        }
        cv2.rectangle(frame, (10, 5), (390, 35), lane_colors[lane], -1)
        cv2.putText(frame, f"LANE {lane}", (140, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add real-time date and time
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, current_time, (50, 280),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Check if ambulance should appear on this lane
        show_ambulance = lane in self.ambulance_lanes
        
        if show_ambulance:
            # Calculate position: full left-to-right traverse over ambulance_traverse_time
            current_time_sec = time.time()
            time_since_ambulance_start = current_time_sec - self.ambulance_start_time
            progress = min(time_since_ambulance_start / ambulance_traverse_time, 1.0)  # 0 to 1, capped at 1
            ambulance_x = int(progress * 350)  # Move from 0 to 350 (leaves frame at right)
            
            # Ambulance body (white rectangle)
            cv2.rectangle(frame, (ambulance_x, 130), (ambulance_x + 50, 160), (255, 255, 255), -1)
            
            # Ambulance roof lights (red)
            cv2.rectangle(frame, (ambulance_x + 8, 122), (ambulance_x + 20, 130), (0, 0, 255), -1)
            cv2.rectangle(frame, (ambulance_x + 30, 122), (ambulance_x + 42, 130), (0, 0, 255), -1)
            
            # Flashing lights
            if int(current_time_sec * 2) % 2 == 0:
                cv2.circle(frame, (ambulance_x + 14, 118), 4, (0, 0, 255), -1)
                cv2.circle(frame, (ambulance_x + 36, 118), 4, (0, 0, 255), -1)
            
            # "AMBULANCE" text
            cv2.putText(frame, "AMBULANCE", (ambulance_x - 10, 180),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Detection box
            cv2.rectangle(frame, (ambulance_x - 5, 120), (ambulance_x + 55, 165), (0, 0, 255), 2)
            
            # Siren indicator (animated)
            siren_intensity = int(100 + 155 * abs(np.sin(current_time_sec * 4)))
            cv2.putText(frame, "SIREN", (ambulance_x - 10, 200),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, siren_intensity, 255), 2)

        # Draw small vehicles for this lane
        # Vehicles stored as dict: {x, type, speed, color, length}
        lane_vehicles = self.vehicles.get(lane, [])
        for v in lane_vehicles:
            x = int(v["x"])
            length = v.get("length", 30)
            h = v.get("h", 20)
            color = v.get("color", (50, 50, 200))
            # Draw body
            cv2.rectangle(frame, (x, 140), (x + length, 140 + h), color, -1)
            # Wheels
            cv2.circle(frame, (x + 8, 140 + h), 3, (0, 0, 0), -1)
            cv2.circle(frame, (x + length - 8, 140 + h), 3, (0, 0, 0), -1)
        
        # Demo mode label
        cv2.putText(frame, "DEMO MODE", (10, 295),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return frame

    def spawn_vehicle(self, lane):
        """Spawn a random vehicle at the left edge for a lane."""
        vtype = random.choice(["car", "truck", "bike"])
        if vtype == "car":
            length = 30
            h = 16
            color = (0, 200, 200)
            speed = random.uniform(1.5, 2.5)
        elif vtype == "truck":
            length = 48
            h = 20
            color = (50, 150, 200)
            speed = random.uniform(1.0, 1.8)
        else:  # bike
            length = 18
            h = 12
            color = (200, 100, 50)
            speed = random.uniform(2.0, 3.0)

        # Start slightly off-screen to the left
        # Apply global speed multiplier
        speed = speed * getattr(self, "speed_multiplier", 1.0)
        vehicle = {"x": -length - random.randint(0, 20), "length": length, "h": h, "color": color, "speed": speed}
        self.vehicles[lane].append(vehicle)
    
    def run_synthetic(self):
        """Generate synthetic ambulance patterns across 4 lanes."""
        print("[DEMO] Running synthetic 4-lane video generator...")
        
        # Parameters
        ambulance_initial_delay = 30.0  # First ambulance after 30 seconds
        ambulance_min_gap = 30.0        # At least 30 seconds between ambulances
        ambulance_duration = 4.0        # Ambulance visible for 4 seconds (3-5s range)
        ambulance_traverse_time = 4.0   # Time for ambulance to traverse full width
        lanes_list = ["N", "E", "S", "W"]
        
        cycle_start = time.time()
        last_ambulance_time = cycle_start - ambulance_initial_delay  # Allow first at 30s
        current_ambulance_lane = None
        ambulance_end_time = 0
        
        while self.running:
            now = time.time()
            elapsed_total = now - cycle_start
            
            # Decide if new ambulance should appear
            time_since_last_ambulance = now - last_ambulance_time
            
            if current_ambulance_lane is None and time_since_last_ambulance >= ambulance_min_gap:
                # Time to spawn new ambulance on a random lane
                current_ambulance_lane = np.random.choice(lanes_list)
                last_ambulance_time = now
                ambulance_end_time = now + ambulance_duration
                self.ambulance_start_time = now
                print(f"[DEMO] Ambulance appeared on lane {current_ambulance_lane}")
            
            # Check if current ambulance should still be visible
            if current_ambulance_lane is not None:
                if now < ambulance_end_time:
                    # Ambulance is visible
                    self.ambulance_lanes = [current_ambulance_lane]
                else:
                    # Ambulance passed
                    current_ambulance_lane = None
                    self.ambulance_lanes = []
                    print(f"[DEMO] Ambulance cleared")
            else:
                self.ambulance_lanes = []

            # Update traffic controller to get latest lights
            try:
                controller.update()
            except Exception:
                pass

            lights = controller.lights.copy()

            # Read runtime vehicle params from shared_state if available
            try:
                with shared_state.lock:
                    params = getattr(shared_state, 'vehicle_params', None)
                    if params is not None:
                        # Validate tuple-like spawn_interval
                        sv = params.get('spawn_interval', None)
                        if sv and isinstance(sv, (list, tuple)) and len(sv) == 2:
                            self.vehicle_spawn_interval = (float(sv[0]), float(sv[1]))
                        self.speed_multiplier = float(params.get('speed_multiplier', 1.0))
            except Exception:
                pass

            # Vehicle spawn & movement logic per lane
            for lane in ["N", "E", "S", "W"]:
                # Spawn vehicles at random intervals
                last_spawn = self.last_vehicle_spawn.get(lane, 0)
                spawn_interval = random.uniform(*self.vehicle_spawn_interval)
                if now - last_spawn > spawn_interval:
                    # Avoid spawning if a vehicle is very near the spawn point
                    too_close = False
                    if self.vehicles[lane]:
                        first = self.vehicles[lane][0]
                        if first["x"] < 0 and first["x"] > -50:
                            too_close = True
                    if not too_close:
                        self.spawn_vehicle(lane)
                        self.last_vehicle_spawn[lane] = now

                # Update vehicle positions according to light
                lane_vehicles = self.vehicles.get(lane, [])
                # Sort vehicles by x descending so we move front-most first
                lane_vehicles.sort(key=lambda v: v["x"], reverse=True)
                for i, v in enumerate(lane_vehicles):
                    # Determine allowed speed based on light
                    state = lights.get(lane, "RED")
                    # Treat PRIORITY as GREEN for the priority lane (controller already sets lights)
                    if state == "GREEN":
                        move_speed = v["speed"]
                    elif state == "YELLOW":
                        move_speed = v["speed"] * 0.6
                    else:
                        move_speed = 0.0

                    # If ambulance on this lane, ensure vehicles stop behind ambulance
                    if lane in self.ambulance_lanes:
                        # compute ambulance x
                        amp_elapsed = now - self.ambulance_start_time
                        amp_progress = min(amp_elapsed / ambulance_traverse_time, 1.0)
                        ambulance_x = int(amp_progress * 350)
                    else:
                        ambulance_x = None

                    # Compute front obstacle x (either next vehicle ahead or ambulance)
                    front_x = None
                    if ambulance_x is not None:
                        front_x = ambulance_x - 10
                    # next vehicle ahead (since sorted desc, vehicle ahead has smaller index)
                    if i > 0:
                        ahead = lane_vehicles[i - 1]
                        front_x = min(front_x, ahead["x"]) if front_x is not None else ahead["x"]

                    # Proposed new x
                    new_x = v["x"] + move_speed
                    # Enforce not passing front_x - length - gap
                    gap = 8
                    if front_x is not None:
                        max_x = front_x - v["length"] - gap
                        if new_x > max_x:
                            new_x = max_x

                    v["x"] = new_x

                # Remove vehicles that left the frame (right beyond 420)
                self.vehicles[lane] = [v for v in lane_vehicles if v["x"] < 420]

            # Generate frames for each lane and publish
            for lane in ["N", "E", "S", "W"]:
                frame = self.generate_test_frame(lane, ambulance_traverse_time)

                with shared_state.lock:
                    shared_state.camera_frames[lane] = frame.copy()
                    shared_state.ambulance_detected[lane] = (lane in self.ambulance_lanes)

                    # Update detections for this lane
                    if lane in self.ambulance_lanes:
                        # Calculate ambulance position (left to right over full duration)
                        current_time_sec = time.time()
                        time_since_ambulance_start = current_time_sec - self.ambulance_start_time
                        progress = min(time_since_ambulance_start / ambulance_traverse_time, 1.0)  # 0 to 1
                        ambulance_x = int(progress * 350)  # Move across full width

                        shared_state.detections[lane] = [{
                            "x1": int(ambulance_x - 5),
                            "y1": 120,
                            "x2": int(ambulance_x + 55),
                            "y2": 165,
                            "label": "ambulance",
                            "conf": 0.95,
                            "is_emergency": True
                        }]
                        shared_state.last_emergency_time = time.time()
                    else:
                        shared_state.detections[lane] = []
            
            time.sleep(0.033)  # ~30 FPS
    
    def run(self):
        """Run appropriate demo mode."""
        self.run_synthetic()

class DemoAudio:
    """Simulates siren detection from audio."""
    
    def __init__(self, audio_path=None):
        self.audio_path = audio_path
        self.running = True
    
    def generate_test_siren(self):
        """Generate synthetic siren audio chunk."""
        sample_rate = 22050
        duration = 0.8  # seconds
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples)
        
        # Siren frequency (sweeps 800-1200 Hz)
        freq_start = 800
        freq_end = 1200
        freq = freq_start + (freq_end - freq_start) * (np.sin(2 * np.pi * 0.5 * t) + 1) / 2
        
        # Generate siren tone
        siren = np.sin(2 * np.pi * freq * t)
        
        # Add harmonics
        siren += 0.5 * np.sin(4 * np.pi * freq * t)
        siren += 0.3 * np.sin(6 * np.pi * freq * t)
        
        # Normalize and add noise
        siren = siren / np.max(np.abs(siren))
        siren = siren * 0.8 + np.random.randn(len(siren)) * 0.05
        
        return siren.astype(np.float32).reshape(-1, 1)
    
    def run_synthetic(self):
        """Generate synthetic siren pattern."""
        print("[DEMO] Running synthetic audio siren generator...")
        
        cycle_on = 2.0   # Seconds of siren on
        cycle_off = 3.0  # Seconds of siren off
        cycle_time = cycle_on + cycle_off
        
        while self.running:
            current_time = time.time() % cycle_time
            is_siren = current_time < cycle_on
            
            with shared_state.lock:
                shared_state.siren_detected = is_siren
                if is_siren:
                    shared_state.last_emergency_time = time.time()
            
            time.sleep(0.1)
    
    def run_audio_file(self):
        """Play audio file and simulate detection."""
        print(f"[DEMO] Opening audio file: {self.audio_path}")
        
        try:
            # Try to load audio file
            import scipy.io.wavfile as wavfile
            sample_rate, audio = wavfile.read(self.audio_path)
            
            if audio.ndim > 1:
                audio = audio[:, 0]  # Take first channel
            
            # Normalize
            audio = audio.astype(np.float32) / np.max(np.abs(audio))
            
            chunk_size = int(0.8 * sample_rate)
            pos = 0
            
            while self.running:
                # Get chunk
                if pos + chunk_size > len(audio):
                    pos = 0  # Loop
                
                chunk = audio[pos:pos + chunk_size]
                
                # Simple siren detection (check frequency content)
                fft = np.fft.rfft(chunk)
                freqs = np.fft.rfftfreq(len(chunk), 1.0 / sample_rate)
                band_mask = (freqs > 500) & (freqs < 2000)
                band_energy = np.sum(np.abs(fft[band_mask]))
                total_energy = np.sum(np.abs(fft)) + 1e-8
                
                is_siren = (band_energy / total_energy) > 0.1
                
                with shared_state.lock:
                    shared_state.siren_detected = is_siren
                    if is_siren:
                        shared_state.last_emergency_time = time.time()
                
                pos += chunk_size
                time.sleep(0.15)
        
        except Exception as e:
            print(f"[ERROR] Could not load audio: {e}")
            print("[DEMO] Falling back to synthetic siren...")
            self.run_synthetic()
    
    def run(self):
        """Run appropriate demo mode."""
        if self.audio_path:
            self.run_audio_file()
        else:
            self.run_synthetic()

def main():
    """Main demo entry point."""
    parser = argparse.ArgumentParser(
        description="Demo mode for Emergency Traffic AI system"
    )
    parser.add_argument("--video", type=str, default=None,
                       help="Path to video file (default: synthetic)")
    parser.add_argument("--audio", type=str, default=None,
                       help="Path to audio file (default: synthetic)")
    parser.add_argument("--generate", action="store_true",
                       help="Generate and save demo video/audio files")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Emergency Traffic AI - DEMO MODE")
    print("=" * 70)
    print("\nDEMO will simulate camera and audio input.")
    print("Run 'python main.py' in another terminal to see UI respond!\n")
    
    if args.generate:
        print("[DEMO] Generating demo files...")
        print("(Feature for future implementation)")
        return
    
    # Start demo camera thread
    camera = DemoCamera(args.video)
    camera_thread = threading.Thread(target=camera.run, daemon=True)
    camera_thread.start()
    print("[DEMO] Camera simulator started")
    
    # Start demo audio thread
    audio = DemoAudio(args.audio)
    audio_thread = threading.Thread(target=audio.run, daemon=True)
    audio_thread.start()
    print("[DEMO] Audio simulator started")
    
    print("\n[DEMO] Running... Press Ctrl+C to stop.\n")
    
    try:
        while True:
            # Print current status
            with shared_state.lock:
                amb = shared_state.ambulance_detected
                lane = shared_state.ambulance_lane
                siren = shared_state.siren_detected
            
            print(f"\r[DEMO] Ambulance: {amb} (Lane: {lane}) | Siren: {siren}", end="", flush=True)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[DEMO] Stopping...")
        camera.running = False
        audio.running = False
        print("[DEMO] Demo stopped.")

if __name__ == "__main__":
    main()
