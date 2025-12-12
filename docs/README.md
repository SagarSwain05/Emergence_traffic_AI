# Emergency Traffic Priority AI System

A desktop application that monitors camera feeds and audio for emergency vehicles (ambulances, fire trucks, police cars), automatically prioritizes their intersection routes via smart traffic light control, and displays real-time status on a Pygame UI.

## Features

- **Camera Detection**: Uses YOLOv8 to detect emergency vehicles and determine which lane they're approaching from (N/E/S/W)
- **Audio Detection**: Analyzes microphone input for siren frequencies (500–2000 Hz) using FFT
- **Smart Traffic Control**: Automatically grants green lights to detected emergency vehicles
- **Live UI**: Pygame-based dashboard showing:
  - 4-way intersection with traffic lights
  - Real-time camera preview
  - Detection status (ambulance + siren)
  - Mode indicator (NORMAL or PRIORITY)
- **Graceful Fallback**: Returns to normal cycling after emergency vehicle passes

## Project Structure

```
emergency_traffic_ai/
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── main.py                    # Main entry point
├── camera_detection.py        # YOLO-based vehicle detection
├── sound_detection.py         # Audio siren detection
├── traffic_controller.py      # Traffic light state machine
├── ui_simulation.py           # Pygame UI rendering
├── utils.py                   # Shared state & threading
├── models/                    # (Optional) Custom trained models
└── assets/
    └── siren_test.wav         # (Optional) Test audio file
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- macOS, Linux, or Windows with webcam and microphone

### Step 1: Clone or Download
```bash
cd ~/Emergence
# (files are already in emergency_traffic_ai/)
```

### Step 2: Create Virtual Environment
```bash
cd emergency_traffic_ai
python -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate        # Windows (PowerShell)
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `ultralytics` – YOLOv8 detector (auto-downloads yolov8n.pt on first run)
- `opencv-python` – Image processing
- `pygame` – UI framework
- `sounddevice` – Microphone input
- `numpy`, `scipy` – Numerical computing
- `torch` – Deep learning backend

**Note**: On first run, YOLOv8 will download ~50 MB model weights. If GPU is available with CUDA, inference will be much faster; CPU-only works but is slower.

### Step 4: Run
```bash
python main.py
```

You should see a Pygame window with:
- A crossroads visualization
- 4 traffic lights (N, E, S, W corners)
- Camera preview (top-right)
- Mode status (NORMAL or PRIORITY)

## How It Works

### Camera Lane Detection
1. Frames from your webcam are captured at ~30 FPS
2. Each frame is resized to 640px width for speed
3. YOLOv8 Nano model detects objects (conf threshold: 0.35)
4. If a detected object label contains "ambulance", "fire", or "police", we track it
5. Bounding box center is mapped to lanes:
   - **Top region (y < 35% height)** → North (N)
   - **Bottom region (y > 65%)** → South (S)
   - **Left region (x < 35% width)** → West (W)
   - **Right region (x > 65%)** → East (E)

### Audio Siren Detection
1. Records 0.8-second chunks from your microphone
2. Computes FFT and checks energy in 500–2000 Hz band (typical siren range)
3. Uses multiple heuristics:
   - Ratio of siren-band energy to total energy > 0.15
   - Detects harmonic peaks (sirens have multiple resonances)
4. Uses moving-average voting (6 chunks) to reduce false positives

### Traffic Control Logic
1. **Normal Mode**: Cycles through lanes every 8 sec green + 2 sec yellow
2. **Priority Mode**: When ambulance or siren is detected:
   - Sets detected lane to GREEN
   - All other lanes to RED
   - Holds priority mode for 3 sec after last detection
   - Returns to Normal after buffer expires

### UI Display
- **Intersection**: Simple gray cross showing roads
- **Traffic Lights**: RGB circles (R=red, Y=yellow, G=green) at each lane
- **Status**: Shows current mode and priority lane (if active)
- **Camera Feed**: 240×180 preview showing live webcam + siren yes/no

## Testing & Tuning

### Test Camera Detection

1. **Show ambulance image/video** to your webcam
2. **Adjust sensitivity** if needed:
   - In `camera_detection.py`, line 54: increase `conf_thresh` to be pickier
   - Default 0.35 is permissive; try 0.5 for stricter detection

3. **If YOLO doesn't recognize your ambulance**:
   - Use the "test mode" to print all detected objects
   - Consider fine-tuning on custom ambulance images (advanced)

### Test Audio Detection

1. **Play siren audio** from another device near your laptop microphone
   - Example: YouTube siren video, or `assets/siren_test.wav` if available

2. **Adjust thresholds** if false positives occur:
   - In `sound_detection.py`, line 21–28:
     - Increase `band_energy > 1e4` threshold
     - Increase `ratio > 0.15` threshold
   - Or lengthen `CHUNK` for more stable FFT

3. **Check microphone input level**:
   - If siren is far away, system may not detect it (total_energy threshold)
   - Increase microphone volume or reduce threshold

### Debugging

Print detection status:
```python
# Run standalone test in terminal
python camera_detection.py
# or
python sound_detection.py
```

To see YOLO boxes on camera (advanced):
- Modify `camera_detection.py` to draw bounding boxes before storing frame
- Use `cv2.rectangle()` to draw on `frame` before storing in `shared_state.camera_frame`

## Performance Tips

- **CPU-only**: YOLO Nano runs ~10–20 FPS on modern laptops. Use `yolov8n.pt` (already set).
- **GPU acceleration**: Install `torch` with CUDA support for 30+ FPS
- **Frame resize**: Currently 640px width. Reduce to 480px for faster, less accurate results.
- **Audio latency**: 0.8 sec per chunk; reduce `CHUNK` for faster response (trade: worse FFT resolution)

## File Reference

| File | Purpose |
|------|---------|
| `main.py` | Entry point; starts threads, runs main loop |
| `camera_detection.py` | YOLO detection thread; maps detections to lanes |
| `sound_detection.py` | Microphone input thread; siren detection |
| `traffic_controller.py` | State machine; manages light cycles |
| `ui_simulation.py` | Pygame renderer; draws UI and camera preview |
| `utils.py` | Shared state + threading locks |

## Optional: Flask Dashboard

If you want a web-based dashboard (e.g., viewing on remote device):
- Stream camera frames as MJPEG
- Show JSON state of traffic lights
- Manually trigger priority mode

I can provide Flask code upon request (see section 9 in original blueprint).

## Advanced Improvements

1. **Better Lane Mapping**: Use homography to project camera view onto fixed lane ROIs
2. **Custom Siren Detector**: Train CNN on mel-spectrograms for higher accuracy
3. **Vehicle Tracking**: Track ambulance across frames to detect exit
4. **Logging & Analytics**: Log timestamps, durations, false positives
5. **Multi-camera Support**: Handle multiple intersections simultaneously

## Troubleshooting

### "Could not open camera"
- Check that your webcam is not in use by another app
- Try `camera_index=1` in `main.py` if you have multiple cameras

### "Import could not be resolved"
- Ensure virtualenv is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Poor detection / false positives
- Check lighting conditions (YOLO works better in daylight)
- Adjust `conf_thresh` in `camera_detection.py` (default 0.35)
- Test with sample images first

### Audio not detecting siren
- Check microphone is working: `python -c "import sounddevice; print(sounddevice.default_device)"`
- Play siren loudly near microphone
- Adjust thresholds in `sound_detection.py` (lines 21–28)

## Next Steps

Pick any of the following to extend this system:

- **A) Add bounding box overlays** – Show detected ambulance boxes on camera preview
- **B) Create Flask dashboard** – Web interface for remote monitoring
- **C) Package for distribution** – Create standalone executable (.exe/.app)
- **D) Multi-intersection support** – Scale to multiple junctions
- **E) Custom YOLO training** – Fine-tune on your specific ambulance images

## License

This project is provided as-is for educational and traffic management purposes.

---

**Questions or issues?** Check the troubleshooting section above, or review the code comments in each module.
