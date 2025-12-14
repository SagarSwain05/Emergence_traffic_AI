# Emergency Traffic Priority AI System

A desktop application that monitors camera feeds and audio for emergency vehicles (ambulances, fire trucks, police cars), automatically prioritizes their intersection routes via smart traffic light control, and displays real-time status on a Pygame UI.

## 📁 Project Structure

The project has been reorganized for better readability:

```
emergency_traffic_ai/
├── src/                       # 📦 All code and dependencies
│   ├── main.py               # Main entry point
│   ├── demo.py               # Demo/testing entry point
│   ├── camera_detection.py   # YOLO-based vehicle detection
│   ├── sound_detection.py    # Audio siren detection
│   ├── traffic_controller.py # Traffic light state machine
│   ├── ui_simulation.py      # Pygame UI rendering
│   ├── utils.py              # Shared state & threading
│   ├── requirements.txt      # Python dependencies
│   ├── venv/                 # Python virtual environment
│   ├── assets/               # Media files (images, audio)
│   ├── models/               # Pre-trained/custom models
│   └── __pycache__/          # Compiled Python files
│
├── docs/                      # 📚 All documentation
│   ├── README.md             # Detailed project documentation
│   ├── START_HERE.md         # Quick start guide
│   ├── COMPLETE_IMPLEMENTATION_GUIDE.md
│   ├── DEPLOYMENT_GUIDE.txt
│   ├── ENHANCEMENTS.md
│   └── ... (other documentation)
│
├── run.py                     # 🚀 Run main application (from root)
├── run_demo.py               # 🎬 Run demo application (from root)
└── THIS_README.md            # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Webcam and microphone
- macOS, Linux, or Windows

### Installation & Setup

1. **Navigate to project**
   ```bash
   cd emergency_traffic_ai
   ```

2. **Create and activate virtual environment** (if not already done)
   ```bash
   python -m venv src/venv
   source src/venv/bin/activate  # macOS/Linux
   # or
   src\venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r src/requirements.txt
   ```

4. **Run the main application**
   ```bash
   python run.py
   ```

   Or run the demo version:
   ```bash
   python run_demo.py
   ```

## 📚 Documentation

For detailed information, see the documentation files in the `docs/` folder:

- **START_HERE.md** - Quick start guide and basic setup
- **README.md** - Complete feature documentation
- **COMPLETE_IMPLEMENTATION_GUIDE.md** - Detailed implementation details
- **DEPLOYMENT_GUIDE.txt** - Deployment instructions
- **ENHANCEMENTS.md** - Feature enhancements and improvements

## 🎯 Features

- **Camera Detection**: Uses YOLOv8 to detect emergency vehicles
- **Audio Detection**: Analyzes microphone input for siren frequencies
- **Smart Traffic Control**: Automatically grants green lights to emergency vehicles
- **Live UI**: Pygame-based dashboard with real-time status
- **Graceful Fallback**: Returns to normal cycling after emergency vehicle passes

## ⚙️ How It Works

1. Camera thread continuously monitors video feed for emergency vehicles
2. Audio thread analyzes microphone input for siren sounds
3. Traffic controller receives detection signals and adjusts lights accordingly
4. UI displays real-time intersection status and detection information

## 🔧 Project Files

| File | Purpose |
|------|---------|
| `src/main.py` | Main application entry point |
| `src/demo.py` | Demo/testing version with simulated data |
| `src/camera_detection.py` | YOLO vehicle detection logic |
| `src/sound_detection.py` | Audio siren detection logic |
| `src/traffic_controller.py` | Traffic light state machine |
| `src/ui_simulation.py` | Pygame UI rendering |
| `src/utils.py` | Shared utilities and threading |

## 📝 Notes

- All Python source files are in the `src/` folder
- All documentation is in the `docs/` folder
- The virtual environment is stored in `src/venv/`
- Dependencies are listed in `src/requirements.txt`
- You can run the application from the root directory using `run.py` or `run_demo.py`

---
## 📽️ Demo View (visit this link)
https://drive.google.com/file/d/1u5NHpRR5KQDwDlBud75yVdnStq_ftbYl/view?usp=sharing

For more details, see **docs/README.md** or **docs/START_HERE.md**
