import cv2
import numpy as np
from typing import List

from app.config import settings
from app_logging.event_logger import log_event


class FaceDetector:
    """
    Face detection module using OpenCV DNN.
    This is designed to be:
    - deterministic
    - fast on CPU
    - edge-friendly
    """

    def __init__(self):
        # Using OpenCV's default Haar Cascade for edge safety
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.detector = cv2.CascadeClassifier(cascade_path)

        if self.detector.empty():
            raise RuntimeError("Failed to load face detection model")

    def detect(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Detects and extracts faces from normalized frames.

        Args:
            frames: List of normalized RGB frames (H, W, 3) in [0,1]

        Returns:
            List of face crops resized to FACE_IMAGE_SIZE
        """

        face_crops = []
        total_faces = 0

        for frame in frames:
            # Convert back to uint8 grayscale for Haar detector
            frame_uint8 = (frame * 255).astype(np.uint8)
            gray = cv2.cvtColor(frame_uint8, cv2.COLOR_RGB2GRAY)

            faces = self.detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(64, 64)
            )

            for (x, y, w, h) in faces:
                face = frame_uint8[y:y+h, x:x+w]

                # Resize face crop to model input size
                face_resized = cv2.resize(
                    face,
                    (settings.FACE_IMAGE_SIZE, settings.FACE_IMAGE_SIZE),
                    interpolation=cv2.INTER_LINEAR
                )

                # Normalize again for model
                face_normalized = face_resized.astype(np.float32) / 255.0
                face_crops.append(face_normalized)
                total_faces += 1

        log_event(
            "FACES_DETECTED",
            {
                "frames_processed": len(frames),
                "faces_detected": total_faces
            }
        )

        return face_crops


# Functional wrapper to match pipeline style
def detect_faces(frames: List[np.ndarray]) -> List[np.ndarray]:
    detector = FaceDetector()
    return detector.detect(frames)
