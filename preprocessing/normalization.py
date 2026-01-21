import cv2
import numpy as np

from app.config import settings
from app_logging.event_logger import log_event


def normalize_frames(frames):
    """
    Normalizes raw video frames for downstream face detection and ML inference.

    Steps:
    - Resize frames to model-compatible size
    - Convert BGR → RGB
    - Normalize pixel values to [0, 1]

    Args:
        frames (list[np.ndarray]): Raw sampled frames

    Returns:
        list[np.ndarray]: Normalized frames
    """

    normalized_frames = []

    for frame in frames:
        # Resize frame
        resized = cv2.resize(
            frame,
            (settings.FACE_IMAGE_SIZE, settings.FACE_IMAGE_SIZE),
            interpolation=cv2.INTER_LINEAR
        )

        # Convert BGR (OpenCV default) → RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        # Normalize pixel values
        normalized = rgb.astype(np.float32) / 255.0

        normalized_frames.append(normalized)

    log_event(
        "FRAMES_NORMALIZED",
        {
            "frame_count": len(normalized_frames),
            "image_size": settings.FACE_IMAGE_SIZE
        }
    )

    return normalized_frames
