# Hand Gesture Recognition 🖐️

A real-time hand gesture recognition system built with **Python**, **OpenCV**, and **MediaPipe** that lets you control your PC's system volume using hand gestures — no hardware controllers needed.

---

## Features

- 🖐️ Real-time hand landmark detection (21 points per hand)
- 🔊 Control system volume by pinching thumb and index finger
- 📏 Live distance measurement between any two landmarks
- 🤞 Finger-state detection (which fingers are up/down)
- 🎯 Bounding box tracking per detected hand
- 📈 FPS overlay for performance monitoring

---

## Project Structure

```
HandGestureRecognition/
│
├── HandTrackingModule.py       # Core reusable hand detector (MediaPipe wrapper)
├── HandGestureRecognition.py   # Standalone gesture visualiser
├── VolumeHandControl.py        # Volume control using HandTrackingModule
├── VolumeControl.py            # Volume control using HandGestureRecognition module
│
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

---

## How It Works

### Hand Detection Pipeline

```
Webcam Frame (BGR)
      │
      ▼
 Convert to RGB
      │
      ▼
 MediaPipe Hands  ──►  21 Landmark Coordinates (x, y, z)
      │
      ▼
 Map to pixel space  ──►  Draw skeleton / bounding box
      │
      ▼
 Gesture logic  ──►  Pinch distance → Volume level
```

### Volume Control Gesture

| Gesture | Action |
|---|---|
| Pinch (thumb + index close) | Low volume |
| Spread (thumb + index apart) | High volume |
| Ring finger down | **Commit** volume change (`VolumeControl.py` only) |

---

## Prerequisites

- Python 3.9 – 3.12
- A webcam connected to your PC
- Windows OS (required for `pycaw` audio control)

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/HandGestureRecognition.git
cd HandGestureRecognition

# 2. (Recommended) Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Basic Hand Tracking

Detects and displays hand landmarks from your webcam:

```bash
python HandTrackingModule.py
```

### Hand Gesture Visualiser

Visualises detected gestures and prints landmark positions:

```bash
python HandGestureRecognition.py
```

### Volume Hand Control (simple pinch)

Continuously maps pinch distance to system volume:

```bash
python VolumeHandControl.py
```

### Volume Control (with commit gesture)

Sets volume only when the ring finger is lowered — prevents accidental changes:

```bash
python VolumeControl.py
```

> Press **Q** to quit any running script.

---

## Key Landmark IDs

```
           8   12  16  20
           |   |   |   |
           7   11  15  19
           |   |   |   |
       4   6   10  14  18
       |   |   |   |   |
   3   5   9   13  17
   |
   2
   |
   1
   |
   0  (wrist)
```

| ID | Landmark |
|---|---|
| 0 | Wrist |
| 4 | Thumb tip |
| 8 | Index finger tip |
| 12 | Middle finger tip |
| 16 | Ring finger tip |
| 20 | Pinky tip |

---

## Dependencies

| Package | Purpose |
|---|---|
| `opencv-python` | Camera capture & image rendering |
| `mediapipe` | Hand landmark detection model |
| `numpy` | Numerical operations & interpolation |
| `pycaw` | Windows Core Audio API wrapper |
| `comtypes` | COM interface for audio endpoint |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Blank / black camera feed | Change `cv2.VideoCapture(0)` to `(1)` or `(2)` |
| `mediapipe` import error | Run `pip install mediapipe>=1.0.0` |
| Audio not changing | Ensure you're on Windows; run as normal user (not admin) |
| Low FPS | Reduce camera resolution (`WCAM`, `HCAM` constants) or lower `detectionCon` |

---

## License

This project is open-source and available under the [MIT License](LICENSE).
