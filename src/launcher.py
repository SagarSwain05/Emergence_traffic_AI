#!/usr/bin/env python3
"""
Emergency Traffic AI - Launcher Menu

Interactive menu to choose which mode to run:
- Basic (with bounding boxes)
- Enhanced visualization
- Web dashboard
- Demo mode
- All together

Makes it easy for new users to get started.
"""

import subprocess
import os
import sys
import time

def print_header():
    print("\n" + "=" * 70)
    print("🚨 Emergency Traffic AI System - Launcher")
    print("=" * 70 + "\n")

def print_menu():
    print("Choose a mode to run:\n")
    print("  1) Basic Desktop UI")
    print("     - Camera preview with bounding boxes")
    print("     - Traffic light display")
    print("     - Detection status")
    print("     → Run: python main.py\n")
    
    print("  2) Enhanced Desktop UI")
    print("     - Larger window (1400×900)")
    print("     - Lane zone visualization")
    print("     - Detection history graphs")
    print("     - Status & analytics panels")
    print("     → Run: python main_enhanced.py\n")
    
    print("  3) Web Dashboard")
    print("     - Access from browser (http://localhost:5000)")
    print("     - Works on phone/tablet")
    print("     - MJPEG camera stream")
    print("     - JSON API for integration")
    print("     → Run: python flask_dashboard.py (+ main.py)\n")
    
    print("  4) Demo Mode (No Hardware Needed!)")
    print("     - Synthetic ambulance animation")
    print("     - Fake siren detection")
    print("     - Perfect for testing")
    print("     → Run: python demo.py (+ main.py in another terminal)\n")
    
    print("  5) Full Stack (All Features)")
    print("     - Basic UI in Terminal 1")
    print("     - Web dashboard in Terminal 2")
    print("     - Demo data in Terminal 3")
    print("     → Multiple terminals\n")
    
    print("  6) Just Setup (No UI)")
    print("     - Install dependencies")
    print("     - Verify hardware")
    print("     - Exit")
    print("     → For custom scripts\n")
    
    print("  0) Exit\n")

def verify_setup():
    """Check if dependencies are installed."""
    print("Checking dependencies...\n")
    
    missing = []
    packages = {
        "numpy": "NumPy",
        "cv2": "OpenCV",
        "pygame": "Pygame",
        "sounddevice": "sounddevice",
        "scipy": "SciPy",
        "ultralytics": "ultralytics (YOLO)",
        "flask": "Flask",
    }
    
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - MISSING")
            missing.append(name)
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print("  pip install -r requirements.txt\n")
        return False
    else:
        print("\n✓ All dependencies installed!\n")
        return True

def check_hardware():
    """Check if camera/microphone are available."""
    print("Checking hardware...\n")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("  ✓ Camera detected")
            cap.release()
            camera_ok = True
        else:
            print("  ✗ Camera not accessible")
            camera_ok = False
    except Exception as e:
        print(f"  ✗ Camera check failed: {e}")
        camera_ok = False
    
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        if devices is not None:
            print(f"  ✓ Microphone detected ({len(devices)} device(s))")
            mic_ok = True
        else:
            print("  ✗ No audio devices found")
            mic_ok = False
    except Exception as e:
        print(f"  ✗ Microphone check failed: {e}")
        mic_ok = False
    
    print()
    
    if not camera_ok:
        print("⚠ Camera not found. Use Demo Mode (option 4) to test without hardware.")
    if not mic_ok:
        print("⚠ Microphone not found. Audio detection will not work.")
    
    print()
    return camera_ok, mic_ok

def run_command(cmd, description=""):
    """Run a shell command."""
    if description:
        print(f"\n{description}")
    print(f"Running: {cmd}\n")
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n\nStopped.")

def main():
    # Check if running from correct directory
    if not os.path.exists("main.py"):
        print("ERROR: This script must be run from the emergency_traffic_ai directory")
        print("Usage: cd emergency_traffic_ai && python launcher.py")
        sys.exit(1)
    
    print_header()
    
    # Initial setup check
    if not verify_setup():
        print("Please install dependencies and try again.")
        sys.exit(1)
    
    camera_ok, mic_ok = check_hardware()
    
    while True:
        print_menu()
        choice = input("Enter choice (0-6): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        
        elif choice == "1":
            run_command("python main.py", 
                       "Starting Emergency Traffic AI (Basic Mode)\nPress Ctrl+C to stop")
        
        elif choice == "2":
            # Check if main_enhanced.py exists, create if not
            if not os.path.exists("main_enhanced.py"):
                print("Creating main_enhanced.py...")
                with open("main_enhanced.py", "w") as f:
                    f.write("""import time
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
        print("Exiting...")

if __name__ == "__main__":
    main_loop()
""")
            run_command("python main_enhanced.py",
                       "Starting Enhanced UI (1400×900 mode)\nPress Ctrl+C to stop")
        
        elif choice == "3":
            print("\n" + "=" * 70)
            print("Flask Dashboard Instructions")
            print("=" * 70)
            print("\nYou need to run TWO terminals:\n")
            print("  Terminal 1: python main.py")
            print("  Terminal 2: python flask_dashboard.py\n")
            print("  Then open: http://localhost:5000 in your browser\n")
            print("=" * 70 + "\n")
            
            ans = input("Would you like to start both now? (y/n): ").strip().lower()
            if ans == "y":
                print("\nStarting main.py first...")
                print("(Keep this running, then start another terminal)\n")
                run_command("python main.py")
            else:
                print("Run 'python flask_dashboard.py' in another terminal while main.py is running.")
        
        elif choice == "4":
            print("\n" + "=" * 70)
            print("Demo Mode (No Hardware Needed)")
            print("=" * 70)
            print("\nYou need to run TWO terminals:\n")
            print("  Terminal 1: python demo.py")
            print("  Terminal 2: python main.py\n")
            print("You'll see a simulated ambulance with auto-generated siren!")
            print("=" * 70 + "\n")
            
            ans = input("Would you like to start demo now? (y/n): ").strip().lower()
            if ans == "y":
                print("\nStarting demo.py first...")
                print("(Keep this running, then start another terminal for main.py)\n")
                run_command("python demo.py")
            else:
                print("Run 'python demo.py' in one terminal and 'python main.py' in another.")
        
        elif choice == "5":
            print("\n" + "=" * 70)
            print("Full Stack Mode (All Features)")
            print("=" * 70)
            print("\nThis requires THREE terminals:\n")
            print("  Terminal 1: python main.py")
            print("  Terminal 2: python flask_dashboard.py")
            print("  Terminal 3: python demo.py")
            print("\nThen:")
            print("  - Main UI: Look at Terminal 1 window")
            print("  - Web: Open http://localhost:5000 in browser")
            print("  - Demo: Keep Terminal 3 running")
            print("\n" + "=" * 70 + "\n")
            
            ans = input("Ready? Open 3 terminals, then press Enter to continue...")
            print("\nYou can now run the commands in each terminal:")
            print("  1. python main.py")
            print("  2. python flask_dashboard.py")
            print("  3. python demo.py")
        
        elif choice == "6":
            print("\n" + "=" * 70)
            print("Setup Complete!")
            print("=" * 70)
            print("\nYou're ready to use the system. Next steps:\n")
            print("  1. Review QUICKSTART_ENHANCEMENTS.md for feature overview")
            print("  2. Read ENHANCEMENTS.md for detailed documentation")
            print("  3. Check README.md for original system info\n")
            print("For custom scripts, you can import:")
            print("  from camera_detection import start_camera_thread")
            print("  from sound_detection import start_audio_thread")
            print("  from traffic_controller import controller")
            print("  from utils import shared_state\n")
        
        else:
            print("Invalid choice. Please try again.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nLauncher interrupted. Goodbye!")
        sys.exit(0)
