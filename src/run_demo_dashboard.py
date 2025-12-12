#!/usr/bin/env python3
"""Run demo simulator and Flask dashboard in the same process.

This script starts the `demo` camera/audio simulator threads so they update
the shared `shared_state` object, then starts the Flask dashboard so the
dashboard's MJPEG stream can read the same shared memory and show live frames.

Usage:
    python run_demo_dashboard.py

"""
import threading
import time
import sys
from demo import DemoCamera, DemoAudio

def start_demo_threads(video=None, audio=None):
    cam = DemoCamera(video)
    cam_thread = threading.Thread(target=cam.run, daemon=True)
    cam_thread.start()

    aud = DemoAudio(audio)
    aud_thread = threading.Thread(target=aud.run, daemon=True)
    aud_thread.start()

    return cam, aud

if __name__ == '__main__':
    print("Starting demo camera/audio threads and Flask dashboard...")
    cam, aud = start_demo_threads()

    # import and run the Flask app (this will block)
    from flask_dashboard import app
    app.run(host='127.0.0.1', port=5001, debug=False, threaded=True)
