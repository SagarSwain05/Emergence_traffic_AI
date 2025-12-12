# QUICKSTART_ENHANCEMENTS.md

Quick guide to using the four new features.

## TL;DR - Try These First

### 1. Bounding Boxes (5 seconds to test)

```bash
python main.py
```

Point your camera at an object. You'll see colored boxes appear around detected objects on the camera preview (top-right of window):
- **Red box** = Emergency vehicle detected
- **Green box** = Other object
- Numbers below = confidence score

### 2. Web Dashboard (2 terminals)

```bash
# Terminal 1
python main.py

# Terminal 2
python flask_dashboard.py
```

Then open browser: **http://localhost:5000**

You'll see:
- Live camera stream with detection boxes
- Traffic light status (colored circles)
- Real-time detection info (ambulance? siren?)
- Auto-updating every 500ms

### 3. Advanced Desktop UI

```bash
# Copy this into a new file called main_enhanced.py
```

See section C in ENHANCEMENTS.md, then:

```bash
python main_enhanced.py
```

Bigger window, more details, lane zones highlighted, detection history graphs.

### 4. Test Without Camera (Demo Mode)

```bash
# Terminal 1 - Synthetic data
python demo.py

# Terminal 2 - See UI respond to fake data
python main.py
```

You'll see animated ambulance moving across the window, fake siren detection.

---

## Comparison Table

| Feature | What You See | Setup Time | CPU Use |
|---------|------------|-----------|---------|
| A) Boxes | Bounding boxes on camera | ✓ Already enabled | 15% |
| B) Dashboard | Web UI in browser | 2 terminals | 25% |
| C) Enhanced | Big fancy desktop UI | Copy 1 file | 20% |
| D) Demo | Fake ambulance on screen | 2 terminals | 10% |

---

## Feature A: Bounding Boxes

### What Changed

- Camera preview now shows what YOLO sees
- Detected objects have colored rectangles
- Confidence score shown

### Where to See It

Run `python main.py` → Look at top-right preview → Bounding boxes appear

### Code Location

- `camera_detection.py` - Collects detection data
- `ui_simulation.py` - Draws boxes on preview

### Example

```
┌─ Ambulance 0.95 ──┐
│  ┌───────────────┐│
│  │    (RED BOX)  ││
│  └───────────────┘│
└───────────────────┘
```

---

## Feature B: Flask Dashboard

### What It Does

Web interface for monitoring. No port/firewall issues, works on phone too.

### Setup (2 commands)

```bash
pip install flask  # Already in requirements.txt

# Terminal 1
python main.py

# Terminal 2
python flask_dashboard.py

# Browser
open http://localhost:5000
```

### What You See

Beautiful dark dashboard with:
- Live camera feed
- Traffic light colors
- Detection status
- Real-time updates

### Accessing Remotely

```bash
# Find your IP (macOS)
ifconfig | grep inet

# On another device on same network
open http://192.168.1.100:5000
```

### API for Integration

```bash
# Get JSON status
curl http://localhost:5000/api/status

# Output
{
  "lights": {"N": "GREEN", "E": "RED", "S": "RED", "W": "YELLOW"},
  "mode": "PRIORITY",
  "ambulance_detected": true,
  ...
}
```

---

## Feature C: Enhanced Visualization

### What It Does

Larger, more detailed desktop UI. Better for monitoring stations.

### Setup (1 file to create)

Create `main_enhanced.py` with this content:

```python
import time
import threading
from camera_detection import start_camera_thread
from sound_detection import start_audio_thread
from traffic_controller import controller
from enhanced_visualization import EnhancedTrafficUI
from utils import shared_state

def main_loop():
    start_camera_thread(0)
    start_audio_thread()
    ui = EnhancedTrafficUI(1400, 900)
    running = True
    try:
        while running:
            for event in __import__("pygame").event.get():
                if event.type == __import__("pygame").QUIT:
                    running = False
            lights, mode, pr = controller.update()
            with shared_state.lock:
                amb_det = shared_state.ambulance_detected
                siren_det = shared_state.siren_detected
                detections = shared_state.detections.copy()
            ui.draw(lights, mode, pr, detections, amb_det, siren_det)
            time.sleep(0.02)
    except KeyboardInterrupt:
        pass
    finally:
        ui.quit()

if __name__ == "__main__":
    main_loop()
```

Then run:

```bash
python main_enhanced.py
```

### What You See

- **Top**: Lane indicators [N] [E] [S] [W]
- **Left**: Camera feed with lane zones
- **Right top**: Detection details (label, confidence)
- **Right bottom**: Status (ambulance? siren? priority lane?)
- **Bottom**: Timeline graphs showing detection history

### Advantages Over Basic UI

- Larger screen area
- Zone visualization (colored regions)
- Confidence bar under each detection
- Detection history graphs
- Better for control rooms

---

## Feature D: Demo Mode

### What It Does

Simulates camera and microphone so you can test without real hardware.

### Setup (1 command)

```bash
# Terminal 1 - Generates fake data
python demo.py

# Terminal 2 - Responds to fake data (in another terminal)
python main.py
```

### What You See

- Animated ambulance moves across camera preview
- Blinking red emergency lights
- Traffic lights automatically prioritize the lane
- Simulated siren (periodic beeping sound indicator)
- Complete system test without real equipment

### With Your Own Video/Audio

```bash
# Use custom video
python demo.py --video /path/to/ambulance.mp4

# Use custom audio
python demo.py --audio /path/to/siren.wav

# Both
python demo.py --video video.mp4 --audio audio.wav
```

### Demo Output

```
[DEMO] Camera simulator started
[DEMO] Audio simulator started
[DEMO] Running... Press Ctrl+C to stop.

[DEMO] Ambulance: True (Lane: N) | Siren: False
[DEMO] Ambulance: True (Lane: N) | Siren: True
[DEMO] Ambulance: True (Lane: E) | Siren: True
[DEMO] Ambulance: False (Lane: None) | Siren: False
```

---

## Combining Features

### Best for Development

```bash
# Terminal 1: Demo (no hardware needed)
python demo.py

# Terminal 2: Main UI (see bounding boxes)
python main.py

# Terminal 3: Web dashboard
python flask_dashboard.py
# open http://localhost:5000
```

### Best for Production

```bash
# Terminal 1: Real system
python main.py

# Terminal 2: Web monitoring
python flask_dashboard.py
# Access from phone at http://<your-ip>:5000
```

### Best for Monitoring Station

```bash
# Terminal 1: Real system
python main.py

# Terminal 2: Enhanced UI (more details)
python main_enhanced.py
```

---

## Troubleshooting

### Bounding Boxes Don't Show

```bash
# Check camera is working
python camera_detection.py

# Look for output:
# Detected: True N
# (means YOLO found something)

# If no detection, try:
# - Better lighting
# - Point at a car (YOLO recognizes cars)
# - Lower confidence threshold in camera_detection.py line 54:
#   conf_thresh=0.25  (from 0.35)
```

### Dashboard Won't Load

```bash
# Make sure Flask is installed
pip install flask

# Port 5000 in use?
lsof -i :5000

# If used, kill it or edit flask_dashboard.py line ~120:
# app.run(host='0.0.0.0', port=5001)  # Change to 5001
```

### Demo Mode Not Working

```bash
# Make sure you're running BOTH:
python demo.py        # Terminal 1
python main.py        # Terminal 2 (separate terminal!)

# Not just one!
```

---

## Next Steps

1. **Try Feature A** (bounding boxes)
   - Run `python main.py`
   - Point camera at something
   - See detection boxes appear

2. **Try Feature D** (demo)
   - Run `python demo.py` + `python main.py`
   - See fake ambulance trigger real traffic lights

3. **Try Feature B** (web)
   - Run both main.py + flask_dashboard.py
   - Open http://localhost:5000 in browser

4. **Try Feature C** (enhanced UI)
   - Create `main_enhanced.py` (copy above)
   - Run `python main_enhanced.py`
   - See detailed analytics

---

## File Reference

| File | Purpose | When to Use |
|------|---------|------------|
| `main.py` | Basic desktop UI (with boxes) | Always first choice |
| `flask_dashboard.py` | Web monitoring | Monitoring station / remote access |
| `main_enhanced.py` | Detailed desktop UI | Control room / more analytics |
| `demo.py` | Simulator (no hardware) | Testing / development |
| `camera_detection.py` | YOLO detection | For inspection/tuning |
| `sound_detection.py` | Siren detection | For inspection/tuning |

---

**Start with A, then try D (demo), then B (web), then C (enhanced)!**
