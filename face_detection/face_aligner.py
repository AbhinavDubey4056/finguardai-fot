import cv2
import numpy as np
from typing import List

from app.config import settings
from app_logging.event_logger import log_event


class FaceAligner:
    """
    Lightweight face alignment module.

    Purpose:
    - Reduce pose variance (tilt / slight rotation)
    - Improve temporal consistency across frames
    - Increase deepfake model stability

    This implementation is edge-safe and does NOT rely on heavy landmark models.
    """

    def __init__(self):
        # Haar-based eye detector (lightweight & offline)
        eye_cascade_path = cv2.data.haarcascades + "haarcascade_eye.xml"
        self.eye_detector = cv2.CascadeClassifier(eye_cascade_path)

        if self.eye_detector.empty():
            raise RuntimeError("Failed to load eye detection model")

    def align_faces(self, faces: List[np.ndarray]) -> List[np.ndarray]:
        """
        Aligns faces based on eye position when possible.

        Args:
            faces: List of face crops (RGB, normalized, fixed size)

        Returns:
            List of aligned face images
        """

        aligned_faces = []
        aligned_count = 0

        for face in faces:
            # Convert to uint8 grayscale for eye detection
            face_uint8 = (face * 255).astype(np.uint8)
            gray = cv2.cvtColor(face_uint8, cv2.COLOR_RGB2GRAY)

            eyes = self.eye_detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(20, 20)
            )

            if len(eyes) >= 2:
                # Take first two detected eyes
                eye1, eye2 = eyes[:2]

                # Compute eye centers
                x1, y1, w1, h1 = eye1
                x2, y2, w2, h2 = eye2

                eye_center_1 = (x1 + w1 // 2, y1 + h1 // 2)
                eye_center_2 = (x2 + w2 // 2, y2 + h2 // 2)

                # Compute angle between eyes
                dy = eye_center_2[1] - eye_center_1[1]
                dx = eye_center_2[0] - eye_center_1[0]
                angle = np.degrees(np.arctan2(dy, dx))

                # Rotate image to align eyes horizontally
                center = (settings.FACE_IMAGE_SIZE // 2,
                          settings.FACE_IMAGE_SIZE // 2)

                rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
                aligned = cv2.warpAffine(
                    face_uint8,
                    rot_mat,
                    (settings.FACE_IMAGE_SIZE, settings.FACE_IMAGE_SIZE),
                    flags=cv2.INTER_LINEAR
                )

                aligned = aligned.astype(np.float32) / 255.0
                aligned_faces.append(aligned)
                aligned_count += 1
            else:
                # If eyes not detected, keep original face
                aligned_faces.append(face)

        log_event(
            "FACES_ALIGNED",
            {
                "faces_input": len(faces),
                "faces_aligned": aligned_count
            }
        )

        return aligned_faces


# Functional wrapper (pipeline-friendly)
def align_faces(faces: List[np.ndarray]) -> List[np.ndarray]:
    aligner = FaceAligner()
    return aligner.align_faces(faces)
