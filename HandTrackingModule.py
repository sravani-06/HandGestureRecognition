"""
Hand Tracking Module — mediapipe Tasks API (compatible with mediapipe >= 0.10.30 / Python 3.13+)
Original by: Murtaza Hassan  |  https://www.computervision.zone
Ported to Tasks API to replace the removed mp.solutions legacy interface.
"""

import math
import os
import time

import cv2
import mediapipe as mp
from mediapipe.tasks import python as _mp_python
from mediapipe.tasks.python import vision as _mp_vision

# ---------------------------------------------------------------------------
# Hand landmark connections (replaces mp.solutions.hands.HAND_CONNECTIONS)
# ---------------------------------------------------------------------------
_HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (0, 9), (9, 10), (10, 11), (11, 12),   # Middle
    (0, 13), (13, 14), (14, 15), (15, 16), # Ring
    (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (5, 9), (9, 13), (13, 17),             # Palm cross-connectors
]

_DEFAULT_MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")
_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)


def _ensure_model(path: str = _DEFAULT_MODEL) -> None:
    """Download the hand landmarker model if it is not present on disk."""
    if not os.path.exists(path):
        import urllib.request
        print(f"[HandTrackingModule] Model not found — downloading to {path} ...")
        urllib.request.urlretrieve(_MODEL_URL, path)
        print("[HandTrackingModule] Model downloaded successfully.")


class handDetector:
    """
    Wraps the mediapipe HandLandmarker Tasks API with the same interface as
    the legacy mp.solutions.hands-based detector so existing scripts need no changes.
    """

    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5,
                 model_path: str = _DEFAULT_MODEL):
        self.tipIds = [4, 8, 12, 16, 20]
        self.lmList = []
        self._detection_result = None

        _ensure_model(model_path)  # auto-download if missing

        options = _mp_vision.HandLandmarkerOptions(
            base_options=_mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=_mp_vision.RunningMode.IMAGE,
            num_hands=int(maxHands),
            min_hand_detection_confidence=float(detectionCon),
            min_hand_presence_confidence=float(detectionCon),
            min_tracking_confidence=float(trackCon),
        )
        self._landmarker = _mp_vision.HandLandmarker.create_from_options(options)

    # ------------------------------------------------------------------
    def findHands(self, img, draw: bool = True):
        """Detect hands in *img* (BGR). Returns annotated *img*."""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        self._detection_result = self._landmarker.detect(mp_img)

        if draw and self._detection_result.hand_landmarks:
            h, w, _ = img.shape
            for hand_lms in self._detection_result.hand_landmarks:
                # Draw skeleton connections
                for s, e in _HAND_CONNECTIONS:
                    x0 = int(hand_lms[s].x * w)
                    y0 = int(hand_lms[s].y * h)
                    x1 = int(hand_lms[e].x * w)
                    y1 = int(hand_lms[e].y * h)
                    cv2.line(img, (x0, y0), (x1, y1), (0, 255, 0), 2)
                # Draw landmark dots
                for lm in hand_lms:
                    cv2.circle(img, (int(lm.x * w), int(lm.y * h)), 5, (255, 0, 255), cv2.FILLED)
        return img

    # ------------------------------------------------------------------
    def findPosition(self, img, handNo: int = 0, draw: bool = True):
        """
        Returns (lmList, bbox) for the hand at index *handNo*.
        lmList: [[id, cx, cy], ...]   bbox: (xmin, ymin, xmax, ymax)
        """
        xList, yList = [], []
        bbox = ()
        self.lmList = []

        if not (self._detection_result and
                self._detection_result.hand_landmarks and
                handNo < len(self._detection_result.hand_landmarks)):
            return self.lmList, bbox

        h, w, _ = img.shape
        hand_lms = self._detection_result.hand_landmarks[handNo]

        for idx, lm in enumerate(hand_lms):
            cx, cy = int(lm.x * w), int(lm.y * h)
            xList.append(cx)
            yList.append(cy)
            self.lmList.append([idx, cx, cy])
            if draw:
                cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        xmin, xmax = min(xList), max(xList)
        ymin, ymax = min(yList), max(yList)
        bbox = (xmin, ymin, xmax, ymax)

        if draw:
            cv2.rectangle(img,
                          (bbox[0] - 20, bbox[1] - 20),
                          (bbox[2] + 20, bbox[3] + 20),
                          (0, 255, 0), 2)
        return self.lmList, bbox

    # ------------------------------------------------------------------
    def fingersUp(self):
        """Returns [1/0] x 5 — 1 means finger is extended."""
        fingers = []
        # Thumb (compare x-axis)
        fingers.append(1 if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1] else 0)
        # Four fingers (compare y-axis; smaller y = higher on screen = extended)
        for i in range(1, 5):
            fingers.append(1 if self.lmList[self.tipIds[i]][2] < self.lmList[self.tipIds[i] - 2][2] else 0)
        return fingers

    # ------------------------------------------------------------------
    def findDistance(self, p1: int, p2: int, img, draw: bool = True):
        """
        Returns (length, img, [x1, y1, x2, y2, cx, cy])
        where length is the Euclidean pixel distance between landmarks p1 and p2.
        """
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]


# ---------------------------------------------------------------------------
def main():
    p_time = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    while True:
        success, img = cap.read()
        if not success:
            break

        img = detector.findHands(img)
        lm_list, _ = detector.findPosition(img)
        if lm_list:
            print(lm_list[4])

        c_time = time.time()
        fps = 1 / (c_time - p_time) if p_time else 0
        p_time = c_time

        cv2.putText(img, f"FPS: {int(fps)}", (10, 70),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow("Hand Tracking", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
