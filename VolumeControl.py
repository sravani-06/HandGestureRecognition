"""
Volume Control (advanced) — uses HandTrackingModule.
Controls system volume via hand gesture: pinch thumb and index finger.
Only sets volume when the ring finger is down (acts as a commit gesture).
"""

import cv2
import numpy as np
import HandTrackingModule as htm
from pycaw.pycaw import AudioUtilities

# ── Camera config ────────────────────────────────────────────────────────────
WCAM, HCAM = 648, 488

cap = cv2.VideoCapture(0)
cap.set(3, WCAM)
cap.set(4, HCAM)

# ── Hand detector ────────────────────────────────────────────────────────────
detector = htm.handDetector(detectionCon=0.7, maxHands=1)

# ── Audio endpoint ───────────────────────────────────────────────────────────
volume = AudioUtilities.GetSpeakers().EndpointVolume
vol_range = volume.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]

# ── State ────────────────────────────────────────────────────────────────────
vol = 0
vol_bar = 400
vol_per = 0
color_vol = (255, 0, 0)

while True:
    success, img = cap.read()
    if not success:
        break

    # Detect hand
    img = detector.findHands(img)
    lm_list, bbox = detector.findPosition(img, draw=True)

    if len(lm_list) != 0:
        # Filter by hand size — reject hands that are too far / too close
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
        if 250 < area < 1000:
            # Distance between thumb tip (4) and index tip (8)
            length, img, line_info = detector.findDistance(4, 8, img)

            # Map distance → volume bar and percentage
            vol_bar = np.interp(length, [50, 200], [400, 150])
            vol_per = np.interp(length, [50, 200], [0, 100])

            # Smooth to nearest 10%
            smoothness = 10
            vol_per = smoothness * round(vol_per / smoothness)

            # Commit volume only when ring finger is down
            fingers = detector.fingersUp()
            if not fingers[3]:
                volume.SetMasterVolumeLevelScalar(vol_per / 100, None)
                cv2.circle(img, (line_info[4], line_info[5]), 15, (0, 255, 0), cv2.FILLED)
                print(f"Volume set to: {vol_per}%")
                color_vol = (0, 0, 255)
            else:
                color_vol = (255, 0, 0)
        else:
            cv2.putText(
                img,
                "Move hand closer",
                (200, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 165, 255),
                2,
            )

        # Volume bar UI
        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (255, 0, 0), cv2.FILLED)
        cv2.putText(
            img, f"{int(vol_per)} %", (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3
        )
        c_vol = int(volume.GetMasterVolumeLevelScalar() * 100)
        cv2.putText(
            img, f"Vol: {c_vol}%", (400, 50), cv2.FONT_HERSHEY_COMPLEX, 1, color_vol, 3
        )

    cv2.imshow("Volume Control", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()