#!/usr/bin/env python3
"""
Quick setup verification script.
Run this after installing dependencies to check that all imports work.

Usage: python verify_setup.py
"""

import sys

def check_imports():
    """Verify all required packages can be imported."""
    packages = [
        ("numpy", "NumPy"),
        ("cv2", "OpenCV"),
        ("pygame", "Pygame"),
        ("sounddevice", "sounddevice"),
        ("scipy", "SciPy"),
        ("ultralytics", "ultralytics (YOLO)"),
    ]
    
    missing = []
    for module, name in packages:
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - NOT FOUND")
            missing.append(name)
    
    return len(missing) == 0

def check_camera():
    """Try to detect camera."""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ Camera detected")
            cap.release()
            return True
        else:
            print("✗ Camera not accessible (may be in use or permission denied)")
            return False
    except Exception as e:
        print(f"✗ Camera check failed: {e}")
        return False

def check_microphone():
    """Try to detect microphone."""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        if devices is not None:
            print(f"✓ Microphone detected ({len(devices)} audio device(s))")
            return True
        else:
            print("✗ No audio devices found")
            return False
    except Exception as e:
        print(f"✗ Microphone check failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Emergency Traffic AI - Setup Verification")
    print("=" * 50)
    print("\n1. Checking Python packages...")
    imports_ok = check_imports()
    
    print("\n2. Checking hardware...")
    camera_ok = check_camera()
    mic_ok = check_microphone()
    
    print("\n" + "=" * 50)
    if imports_ok and camera_ok and mic_ok:
        print("✓ All checks passed! Ready to run: python main.py")
        sys.exit(0)
    else:
        print("✗ Some checks failed. See above for details.")
        if not imports_ok:
            print("  → Run: pip install -r requirements.txt")
        sys.exit(1)
