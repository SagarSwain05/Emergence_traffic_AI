# 📁 Project Structure Overview

## Directory Tree

```
emergency_traffic_ai/
│
├── 📄 README.md                          # 👈 START HERE - Project overview & quick start
├── 📄 REORGANIZATION_GUIDE.md            # Explanation of the restructuring
│
├── 📂 src/                               # 🔧 ALL CODE & DEPENDENCIES
│   ├── 📄 main.py                        # Main application entry point
│   ├── 📄 demo.py                        # Demo/simulation mode
│   ├── 📄 camera_detection.py            # YOLO-based vehicle detection
│   ├── 📄 sound_detection.py             # Audio siren detection
│   ├── 📄 traffic_controller.py          # Traffic light state machine
│   ├── 📄 ui_simulation.py               # Pygame UI rendering
│   ├── 📄 utils.py                       # Shared state & utilities
│   ├── 📄 enhanced_visualization.py      # Enhanced UI features
│   ├── 📄 flask_dashboard.py             # Web dashboard interface
│   ├── 📄 launcher.py                    # Alternative launcher
│   ├── 📄 monitor_status.py              # Status monitoring
│   ├── 📄 run_demo_dashboard.py          # Dashboard demo
│   ├── 📄 verify_setup.py                # Setup verification
│   │
│   ├── 📄 requirements.txt               # Python package dependencies
│   ├── 📂 venv/                          # Python virtual environment
│   ├── 📂 assets/                        # Media files (images, audio)
│   ├── 📂 models/                        # Pre-trained & custom ML models
│   └── 📂 __pycache__/                   # Compiled Python cache
│
├── 📂 docs/                              # 📚 ALL DOCUMENTATION
│   ├── 📄 README.md                      # Detailed project documentation
│   ├── 📄 START_HERE.md                  # Quick start guide
│   ├── 📄 COMPLETE_IMPLEMENTATION_GUIDE.md
│   ├── 📄 DEPLOYMENT_GUIDE.txt
│   ├── 📄 ENHANCEMENTS.md
│   ├── 📄 COMPLETE_FEATURE_SUMMARY.md
│   ├── 📄 IMPLEMENTATION_GUIDE_SUMMARY.md
│   ├── 📄 QUICKSTART_ENHANCEMENTS.md
│   ├── 📄 QUICK_REFERENCE_CARD.md
│   ├── 📄 VISUAL_GUIDE.md
│   ├── 📄 DOCUMENTATION_INDEX.md
│   └── 📄 COMPLETION_SUMMARY.md
│
├── 🚀 run.py                             # Quick launcher for main app
└── 🎬 run_demo.py                        # Quick launcher for demo mode
```

## Quick Access Guide

### 🎯 Getting Started
1. Read **README.md** (root level)
2. Read **docs/START_HERE.md** for setup instructions
3. Run `python run.py` to start the application

### 💻 Code Files (in `src/`)
| File | Purpose |
|------|---------|
| `main.py` | Main application with real camera/audio |
| `demo.py` | Demo mode with simulated data |
| `camera_detection.py` | YOLOv8 vehicle detection logic |
| `sound_detection.py` | Microphone siren detection |
| `traffic_controller.py` | Traffic light control logic |
| `ui_simulation.py` | Pygame interface |
| `utils.py` | Shared state, threading utilities |

### 📚 Documentation Files (in `docs/`)
| File | Purpose |
|------|---------|
| `README.md` | Full project documentation |
| `START_HERE.md` | Installation & quick start |
| `COMPLETE_IMPLEMENTATION_GUIDE.md` | Technical deep dive |
| `DEPLOYMENT_GUIDE.txt` | Deployment instructions |
| `ENHANCEMENTS.md` | Feature improvements |

### 🔧 Environment & Dependencies
- **Virtual Environment**: `src/venv/`
- **Dependencies**: `src/requirements.txt`
- **Assets**: `src/assets/` (images, audio files)
- **Models**: `src/models/` (ML models)

## 🚀 Running the Project

### From Project Root:
```bash
# Activate virtual environment
source src/venv/bin/activate

# Install dependencies (first time)
pip install -r src/requirements.txt

# Run main application
python run.py

# Or run demo mode
python run_demo.py
```

### Or from within `src/` directory:
```bash
python main.py        # Run main app
python demo.py        # Run demo
python flask_dashboard.py  # Run web dashboard
```

## 📊 File Organization Benefits

✅ **Cleaner Code Access**: All `.py` files in one place  
✅ **Easier Documentation Reading**: All `.md` files organized  
✅ **Better Project Navigation**: Clear separation of concerns  
✅ **Maintained Functionality**: No code changes needed  
✅ **Professional Structure**: Industry-standard organization  

## 🔗 Key Locations

| Need | Location |
|------|----------|
| To edit code | `src/` |
| To read docs | `docs/` |
| To run app | `python run.py` (from root) |
| To check setup | `src/verify_setup.py` |
| To see config | `src/requirements.txt` |
| Environment | `src/venv/` |

---

**Next Steps**: Open **docs/START_HERE.md** or read **docs/README.md** for detailed instructions.
