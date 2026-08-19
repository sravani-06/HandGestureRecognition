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
├── HandTrackingModule.py       # Core reusable hand detector (single source of truth)
├── VolumeHandControl.py        # Simple pinch → volume (continuous)
├── VolumeControl.py            # Pinch + commit gesture → volume (deliberate)
│
├── hand_landmarker.task        # MediaPipe hand landmark model (auto-downloaded)
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
 Convert to RGB → mp.Image
      │
      ▼
 MediaPipe HandLandmarker  ──►  21 Landmark Coordinates (x, y, z) per hand
      │
      ▼
 Map to pixel space  ──►  Draw skeleton / bounding box
      │
      ▼
 Gesture logic  ──►  Pinch distance → Volume level
```

### Volume Control Gestures

| Gesture | Action |
|---|---|
| Pinch (thumb + index close) | Low volume |
| Spread (thumb + index apart) | High volume |
| Ring finger down | **Commit** volume change (`VolumeControl.py` only) |

### Script Comparison

| | `VolumeHandControl.py` | `VolumeControl.py` |
|---|---|---|
| **Trigger** | Every frame (continuous) | Ring finger down (deliberate) |
| **Smoothing** | None | Rounds to nearest 10% |
| **Hand filter** | None | Rejects hand if too close/far |
| **Use case** | Quick direct control | Accident-resistant control |

---

## Prerequisites

- Python 3.9+  (tested on 3.13)
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

# 4. Download the MediaPipe hand landmark model
python -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task', 'hand_landmarker.task'); print('Model downloaded.')"
```

> **Note:** The `hand_landmarker.task` model file is required by the MediaPipe Tasks API.
> If you already have it in the project root, skip step 4.

---

## Usage

### Basic Hand Tracking

Detects and displays hand landmarks from your webcam:

```bash
python HandTrackingModule.py
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

| Package | Version | Purpose |
|---|---|---|
| `opencv-python` | ≥ 4.8.0 | Camera capture & image rendering |
| `mediapipe` | 0.10.30 – 0.10.35 | Hand landmark detection (Tasks API) |
| `numpy` | ≥ 1.24.0 | Numerical operations & interpolation |
| `pycaw` | ≥ 20230407 | Windows Core Audio API wrapper |

> **Why mediapipe 0.10.x?**  
> mediapipe 1.0+ on Python 3.13/Windows removed the legacy `mp.solutions` namespace.
> This project uses the Tasks API (`HandLandmarker`) which is available from 0.10.30 onward.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `module 'mediapipe' has no attribute 'solutions'` | Use mediapipe 0.10.30–0.10.35: `pip install "mediapipe==0.10.35"` |
| `'AudioDevice' has no attribute 'Activate'` | pycaw API changed — already fixed; update to latest code |
| `hand_landmarker.task` not found | Run the model download command in step 4 of Installation |
| Blank / black camera feed | Change `cv2.VideoCapture(0)` to `(1)` or `(2)` |
| Audio not changing | Ensure you're on Windows; run as normal user (not admin) |
| Low FPS | Reduce camera resolution (`WCAM`, `HCAM`) or lower `detectionCon` |
| `W0000 inference_feedback_manager` warnings | Harmless MediaPipe internal warnings — safe to ignore |

---

## License

This project is open-source and available under the [MIT License](LICENSE).
