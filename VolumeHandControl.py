"""
Volume Hand Control — uses HandTrackingModule.
Controls system volume by tracking the distance between thumb tip and index
finger tip. Displays FPS and a live volume bar overlay.
"""

import cv2
import time
import numpy as np
import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# ── Camera config ────────────────────────────────────────────────────────────
WCAM, HCAM = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, WCAM)
cap.set(4, HCAM)

# ── Audio endpoint ───────────────────────────────────────────────────────────
detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

vol_range = volume.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]

# ── State ────────────────────────────────────────────────────────────────────
vol = 0
vol_bar = 400
vol_per = 0
p_time = 0

while True:
    success, img = cap.read()
    if not success:
        break

    img = detector.findHands(img)
    lm_list, bbox = detector.findPosition(img, draw=False)

    if len(lm_list) != 0:
        x1, y1 = lm_list[4][1], lm_list[4][2]   # Thumb tip
        x2, y2 = lm_list[8][1], lm_list[8][2]   # Index tip
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Draw pinch visualisation
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = np.hypot(x2 - x1, y2 - y1)

        # Map pinch distance → volume
        vol = np.interp(length, [50, 300], [min_vol, max_vol])
        vol_bar = np.interp(length, [50, 300], [400, 150])
        vol_per = np.interp(length, [50, 300], [0, 100])

        volume.SetMasterVolumeLevel(vol, None)
        print(f"Pinch: {int(length)}px  |  Volume: {int(vol_per)}%")

        # Pinch-closed indicator
        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    # Volume bar
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(
        img, f"{int(vol_per)} %", (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3
    )

    # FPS counter
    c_time = time.time()
    fps = 1 / (c_time - p_time) if p_time else 0
    p_time = c_time
    cv2.putText(
        img, f"FPS: {int(fps)}", (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3
    )

    cv2.imshow("Volume Hand Control", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()