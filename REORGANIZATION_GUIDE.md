# Project Reorganization Guide

## 📊 What Changed?

The project structure has been reorganized for better code organization and documentation readability:

### Before
```
emergency_traffic_ai/
├── *.py files (mixed with docs)
├── *.md files (mixed with code)
├── *.txt files
├── requirements.txt
├── venv/
├── assets/
├── models/
└── __pycache__/
```

### After
```
emergency_traffic_ai/
├── src/                  # All code and dependencies
│   ├── *.py files
│   ├── requirements.txt
│   ├── venv/
│   ├── assets/
│   ├── models/
│   └── __pycache__/
├── docs/                 # All documentation
│   ├── README.md
│   ├── START_HERE.md
│   └── ...
├── run.py               # Main launcher (from root)
├── run_demo.py          # Demo launcher (from root)
└── README.md            # Root-level overview
```

## ✅ Benefits

1. **Better Code Organization**: All Python code in one place
2. **Clearer Documentation**: All docs in dedicated folder
3. **Easier Navigation**: Clear separation of concerns
4. **Maintained Functionality**: All imports and execution work the same
5. **Easy to Run**: Launch from root with `python run.py`

## 🚀 How to Use

### Running the Application

From the project root directory:

```bash
# Activate virtual environment (if needed)
source src/venv/bin/activate

# Run main application
python run.py

# Run demo version
python run_demo.py
```

### Installing Dependencies

```bash
source src/venv/bin/activate
pip install -r src/requirements.txt
```

### Accessing Code

All Python source files are in `src/`:
- `src/main.py` - Main entry point
- `src/camera_detection.py` - Vehicle detection
- `src/sound_detection.py` - Siren detection
- `src/traffic_controller.py` - Traffic logic
- `src/ui_simulation.py` - UI rendering
- `src/utils.py` - Utilities
- etc.

### Accessing Documentation

All documentation is in `docs/`:
- `docs/README.md` - Full project documentation
- `docs/START_HERE.md` - Quick start guide
- `docs/COMPLETE_IMPLEMENTATION_GUIDE.md` - Technical details
- etc.

## 🔧 Technical Details

### Import Path Handling

The launcher scripts (`run.py` and `run_demo.py`) automatically add `src/` to the Python path:

```python
import sys
import os
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)
```

This allows all imports within `src/` to work exactly as before, since all Python files are in the same directory.

### No Code Changes Required

- All Python files remain unchanged
- All imports (e.g., `from utils import shared_state`) work exactly as before
- Virtual environment is still in `src/venv/`
- Dependencies remain the same


To get started, see **docs/START_HERE.md** or run `python run.py` from the project root.
