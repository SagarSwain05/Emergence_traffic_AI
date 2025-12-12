# flask_dashboard.py
"""
Optional Flask web dashboard for remote monitoring.

Provides:
- MJPEG stream of camera feed (with YOLO detections)
- JSON endpoint for traffic light state
- Web interface showing real-time status

Run: python flask_dashboard.py
Then visit: http://localhost:5000

Note: Run alongside main.py (in separate terminal/thread)
"""

from flask import Flask, render_template_string, Response, jsonify
import cv2
import numpy as np
import threading
from utils import shared_state
import time

app = Flask(__name__)

# HTML template for dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Emergency Traffic AI Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            color: #fff;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            margin-bottom: 20px;
            font-size: 2.5em;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        .stream-card {
            grid-column: 1;
        }
        .status-card {
            grid-column: 2;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
        }
        .status-row {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: rgba(0,0,0,0.3);
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .status-label { font-weight: bold; }
        .status-value {
            font-size: 1.2em;
            font-weight: bold;
            color: #00ff00;
        }
        .status-value.red { color: #ff4444; }
        .status-value.yellow { color: #ffff00; }
        .stream-container {
            position: relative;
            width: 100%;
            overflow: hidden;
            border-radius: 8px;
        }
        .stream-img {
            width: 100%;
            height: auto;
            display: block;
        }
        .lights-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-top: 20px;
        }
        .light-box {
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        .light-indicator {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            margin: 0 auto 10px;
            border: 3px solid rgba(255,255,255,0.3);
        }
        .light-indicator.red { background: #ff4444; }
        .light-indicator.yellow { background: #ffff00; }
        .light-indicator.green { background: #44ff44; }
        .light-label { font-weight: bold; font-size: 1.2em; }
        .mode-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 10px;
        }
        .mode-badge.normal { background: #4444ff; }
        .mode-badge.priority { background: #ff4444; }
        .refresh-rate { text-align: center; font-size: 0.9em; color: #aaa; margin-top: 10px; }
    </style>
    <script>
        // Simple single-frame polling for all 4 lanes
        class FramePoller {
            constructor(lane, canvasId) {
                this.lane = lane;
                this.canvas = document.getElementById(canvasId);
                this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
                this.running = true;
                if (this.canvas) {
                    this.start();
                }
            }
            
            start() {
                if (!this.running || !this.canvas) return;
                
                const img = new Image();
                img.crossOrigin = 'anonymous';
                
                // Fetch single JPEG frame
                img.onload = () => {
                    try {
                        if (this.ctx) {
                            this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
                        }
                    } catch (e) {
                        console.error(`Draw error (lane ${this.lane}):`, e);
                    }
                    // Poll next frame after 100ms
                    setTimeout(() => this.start(), 100);
                };
                
                img.onerror = () => {
                    console.warn(`Frame load error (lane ${this.lane})`);
                    setTimeout(() => this.start(), 500);
                };
                
                // Use frame endpoint with cache-busting timestamp
                img.src = `/frame/${this.lane}?t=${Date.now()}`;
            }
            
            stop() {
                this.running = false;
            }
        }
        
        // Start frame pollers for all lanes when page loads
        window.addEventListener('load', function() {
            console.log('Starting frame pollers for all 4 lanes...');
            window.pollers = {
                N: new FramePoller('N', 'canvas-N'),
                E: new FramePoller('E', 'canvas-E'),
                S: new FramePoller('S', 'canvas-S'),
                W: new FramePoller('W', 'canvas-W')
            };
            console.log('All frame pollers started');
        });
        
        // Update status
        function updateStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    for (const lane of ['N', 'E', 'S', 'W']) {
                        const light = document.getElementById(`light-${lane}`);
                        const state = data.lights[lane];
                        light.className = `light-indicator ${state.toLowerCase()}`;
                        
                        const ambulanceEl = document.getElementById(`ambulance-${lane}`);
                        ambulanceEl.textContent = data.ambulance_detected[lane] ? '🚑 AMBULANCE' : 'No Ambulance';
                        ambulanceEl.style.color = data.ambulance_detected[lane] ? '#ff0000' : '#888888';
                    }
                    
                    const modeEl = document.getElementById('mode-badge');
                    modeEl.textContent = data.mode;
                    modeEl.style.color = data.mode === 'PRIORITY' ? '#ff0000' : '#ffff00';
                    
                    document.getElementById('priority-lane').textContent = data.priority_lane || 'None';
                    document.getElementById('priority-lane').style.color = data.priority_lane ? '#ff0000' : '#00ff00';
                })
                .catch(e => console.error("Status update failed:", e));
        }
        
        setInterval(updateStatus, 500);
        updateStatus();
    </script>
</head>
<body>
    <div class="container">
        <h1>🚨 Emergency Traffic AI Dashboard</h1>
        
        <h2 style="text-align: center; margin-bottom: 20px;">📹 4-Lane Camera Feeds</h2>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 30px;">
            <div class="card">
                <h3 style="text-align: center; color: #ff6b6b;">North Lane</h3>
                <div class="stream-container">
                    <canvas id="canvas-N" width="400" height="300" style="width: 100%; height: auto; background: #222;"></canvas>
                </div>
            </div>
            <div class="card">
                <h3 style="text-align: center; color: #4ecdc4;">East Lane</h3>
                <div class="stream-container">
                    <canvas id="canvas-E" width="400" height="300" style="width: 100%; height: auto; background: #222;"></canvas>
                </div>
            </div>
            <div class="card">
                <h3 style="text-align: center; color: #ffe66d;">South Lane</h3>
                <div class="stream-container">
                    <canvas id="canvas-S" width="400" height="300" style="width: 100%; height: auto; background: #222;"></canvas>
                </div>
            </div>
            <div class="card">
                <h3 style="text-align: center; color: #95e1d3;">West Lane</h3>
                <div class="stream-container">
                    <canvas id="canvas-W" width="400" height="300" style="width: 100%; height: auto; background: #222;"></canvas>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2 style="text-align: center;">🚦 Traffic Light Status</h2>
            <div class="lights-grid">
                <div class="light-box">
                    <div id="light-N" class="light-indicator"></div>
                    <div class="light-label">North</div>
                    <div id="ambulance-N" style="font-size: 0.8em; color: #ff6b6b; margin-top: 5px;">No Ambulance</div>
                </div>
                <div class="light-box">
                    <div id="light-E" class="light-indicator"></div>
                    <div class="light-label">East</div>
                    <div id="ambulance-E" style="font-size: 0.8em; color: #4ecdc4; margin-top: 5px;">No Ambulance</div>
                </div>
                <div class="light-box">
                    <div id="light-S" class="light-indicator"></div>
                    <div class="light-label">South</div>
                    <div id="ambulance-S" style="font-size: 0.8em; color: #ffe66d; margin-top: 5px;">No Ambulance</div>
                </div>
                <div class="light-box">
                    <div id="light-W" class="light-indicator"></div>
                    <div class="light-label">West</div>
                    <div id="ambulance-W" style="font-size: 0.8em; color: #95e1d3; margin-top: 5px;">No Ambulance</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 20px; font-size: 1.1em;">
                <span style="margin-right: 20px;">Mode: <span id="mode-badge" style="font-weight: bold; color: #ffff00;">LOADING</span></span>
                <span>Priority Lane: <span id="priority-lane" style="font-weight: bold; color: #00ff00;">None</span></span>
            </div>
        </div>
        
        <div class="card">
            <h2 style="text-align: center;">🚗 Vehicle Simulation Controls</h2>
            <div style="display:flex; gap:12px; align-items:center; justify-content:center; margin-top:10px;">
                <label>Spawn interval (min - max sec):</label>
                <input id="spawn-min" type="number" step="0.1" style="width:80px;" />
                <input id="spawn-max" type="number" step="0.1" style="width:80px;" />
                <label style="margin-left:12px;">Speed multiplier:</label>
                <input id="speed-mult" type="number" step="0.1" style="width:80px;" />
                <button id="apply-vehicles">Apply</button>
            </div>
            <div style="text-align:center; margin-top:10px; color:#aaa; font-size:0.9em;">Change take effect immediately across all lanes.</div>
        </div>
        
        <div class="refresh-rate">Updates every 500ms | Refresh your browser if stream stops</div>
    </div>
    <script>
        // Vehicle controls: load current params and apply updates
        function loadVehicleParams() {
            fetch('/api/vehicle_params')
                .then(r => r.json())
                .then(p => {
                    const sv = p.spawn_interval || [2.0,5.0];
                    document.getElementById('spawn-min').value = sv[0];
                    document.getElementById('spawn-max').value = sv[1];
                    document.getElementById('speed-mult').value = p.speed_multiplier || 1.0;
                })
                .catch(e => console.warn('Could not load vehicle params', e));
        }

        document.getElementById('apply-vehicles').addEventListener('click', function() {
            const min = parseFloat(document.getElementById('spawn-min').value) || 1.0;
            const max = parseFloat(document.getElementById('spawn-max').value) || 5.0;
            const mult = parseFloat(document.getElementById('speed-mult').value) || 1.0;

            const body = { spawn_interval: [min, max], speed_multiplier: mult };
            fetch('/api/vehicle_params', {
                method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)
            }).then(r => r.json()).then(resp => {
                console.log('Vehicle params updated', resp);
                // Brief UI feedback
                const btn = document.getElementById('apply-vehicles');
                btn.textContent = 'Applied';
                setTimeout(() => btn.textContent = 'Apply', 800);
            }).catch(e => console.error('Update failed', e));
        });

        // Load current params on start
        window.addEventListener('load', () => setTimeout(loadVehicleParams, 200));
    </script>
</body>
</html>
"""

def generate_frames():
    """Generate MJPEG streams - now returns dict with 4 lanes."""
    # This will be called by 4 separate routes: /video_feed/N, /video_feed/E, /video_feed/S, /video_feed/W
    # We'll refactor this to be lane-specific
    pass

def generate_frames_for_lane(lane):
    """Generate MJPEG stream for a specific lane."""
    while True:
        try:
            with shared_state.lock:
                frame = shared_state.camera_frames[lane].copy() if shared_state.camera_frames[lane] is not None else None
                detections = shared_state.detections[lane].copy() if shared_state.detections[lane] else []
            
            # If no frame, generate a placeholder
            if frame is None:
                frame = np.ones((300, 400, 3), dtype=np.uint8) * 50
                cv2.putText(frame, f"Lane {lane}", (150, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv2.putText(frame, "Waiting for feed...", (100, 180),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 1)
            
            # Draw detections directly on frame
            frame_with_boxes = frame.copy()
            for det in detections:
                x1, y1, x2, y2 = det.get("x1", 0), det.get("y1", 0), det.get("x2", 0), det.get("y2", 0)
                label = det.get("label", "unknown")
                conf = det.get("conf", 0.0)
                is_emergency = det.get("is_emergency", False)
                
                # Use bright red for emergency vehicles, green for others
                if is_emergency:
                    color = (0, 0, 255)  # Red in BGR
                    thickness = 3
                else:
                    color = (0, 255, 0)  # Green in BGR
                    thickness = 2
                
                # Draw bounding box
                cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), color, thickness)
                
                # Draw label with confidence
                label_text = f"{label} {conf:.2f}"
                cv2.putText(frame_with_boxes, label_text, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Ensure frame is correct size
            if frame_with_boxes.shape != (300, 400, 3):
                frame_with_boxes = cv2.resize(frame_with_boxes, (400, 300))
            
            # Encode to JPEG
            ret, buffer = cv2.imencode('.jpg', frame_with_boxes, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                time.sleep(0.01)
                continue
            frame_bytes = buffer.tobytes()
            
            # Yield in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n'
                   + frame_bytes + b'\r\n')
            
            time.sleep(0.033)  # ~30 FPS
        except Exception as e:
            print(f"Stream error (lane {lane}): {e}")
            import traceback
            traceback.print_exc()
            time.sleep(0.1)

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed/<lane>')
def video_feed(lane):
    """MJPEG video stream endpoint for a specific lane (N/E/S/W)."""
    if lane not in ['N', 'E', 'S', 'W']:
        return "Invalid lane", 404
    return Response(generate_frames_for_lane(lane), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/frame/<lane>')
def get_frame(lane):
    """Get a single JPEG frame for a specific lane (N/E/S/W)."""
    if lane not in ['N', 'E', 'S', 'W']:
        return "Invalid lane", 404
    
    try:
        with shared_state.lock:
            frame = shared_state.camera_frames[lane].copy() if shared_state.camera_frames[lane] is not None else None
            detections = shared_state.detections[lane].copy() if shared_state.detections[lane] else []
        
        # If no frame, generate a placeholder
        if frame is None:
            frame = np.ones((300, 400, 3), dtype=np.uint8) * 50
            cv2.putText(frame, f"Lane {lane}", (150, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            cv2.putText(frame, "Waiting for feed...", (100, 180),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 1)
        
        # Draw detections directly on frame
        frame_with_boxes = frame.copy()
        for det in detections:
            x1, y1, x2, y2 = det.get("x1", 0), det.get("y1", 0), det.get("x2", 0), det.get("y2", 0)
            label = det.get("label", "unknown")
            conf = det.get("conf", 0.0)
            is_emergency = det.get("is_emergency", False)
            
            # Use bright red for emergency vehicles, green for others
            if is_emergency:
                color = (0, 0, 255)  # Red in BGR
                thickness = 3
            else:
                color = (0, 255, 0)  # Green in BGR
                thickness = 2
            
            # Draw bounding box
            cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), color, thickness)
            
            # Draw label with confidence
            label_text = f"{label} {conf:.2f}"
            cv2.putText(frame_with_boxes, label_text, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Ensure frame is correct size
        if frame_with_boxes.shape != (300, 400, 3):
            frame_with_boxes = cv2.resize(frame_with_boxes, (400, 300))
        
        # Encode to JPEG
        ret, buffer = cv2.imencode('.jpg', frame_with_boxes, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            raise Exception("Failed to encode frame")
        
        return Response(buffer.tobytes(), mimetype='image/jpeg')
    except Exception as e:
        print(f"Frame error (lane {lane}): {e}")
        # Return a 1x1 placeholder image on error
        placeholder = np.ones((100, 100, 3), dtype=np.uint8) * 25
        ret, buffer = cv2.imencode('.jpg', placeholder)
        return Response(buffer.tobytes(), mimetype='image/jpeg')

@app.route('/api/status')
def api_status():
    """JSON API endpoint for current system status."""
    from traffic_controller import controller
    
    # Update controller state based on shared_state (this makes lights respond)
    controller.update()
    
    with shared_state.lock:
        lights = controller.lights.copy()
        mode = controller.mode
        priority_lane = controller.priority_lane
        
        # Build ambulance detected per lane
        ambulance_detected = {
            "N": shared_state.ambulance_detected["N"],
            "E": shared_state.ambulance_detected["E"],
            "S": shared_state.ambulance_detected["S"],
            "W": shared_state.ambulance_detected["W"]
        }
    
    return jsonify({
        "lights": lights,
        "mode": mode,
        "priority_lane": priority_lane,
        "ambulance_detected": ambulance_detected,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route('/api/vehicle_params', methods=['GET'])
def api_get_vehicle_params():
    with shared_state.lock:
        params = getattr(shared_state, 'vehicle_params', {"spawn_interval": (2.0,5.0), "speed_multiplier": 1.0})
    # Convert tuples to lists for JSON
    p = {"spawn_interval": list(params.get('spawn_interval', (2.0,5.0))), "speed_multiplier": float(params.get('speed_multiplier', 1.0))}
    return jsonify(p)


@app.route('/api/vehicle_params', methods=['POST'])
def api_set_vehicle_params():
    from flask import request
    try:
        data = request.get_json() or {}
        sv = data.get('spawn_interval', None)
        mult = float(data.get('speed_multiplier', 1.0))

        if sv is None or not isinstance(sv, (list, tuple)) or len(sv) != 2:
            return jsonify({"error": "spawn_interval must be [min, max]"}), 400

        sv0 = float(sv[0]); sv1 = float(sv[1])
        if sv0 <= 0 or sv1 <= 0 or sv0 >= sv1:
            return jsonify({"error": "Invalid spawn interval range"}), 400

        with shared_state.lock:
            shared_state.vehicle_params = {"spawn_interval": (sv0, sv1), "speed_multiplier": mult}

        return jsonify({"ok": True, "spawn_interval": [sv0, sv1], "speed_multiplier": mult})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("=" * 60)
    print("Flask Dashboard starting...")
    print("=" * 60)
    print("\nOpen your browser to: http://localhost:5000")
    print("\nMake sure main.py is running in another terminal!")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
