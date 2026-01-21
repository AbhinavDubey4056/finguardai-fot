import torch
import numpy as np
from typing import List

from inference.model_loader import get_model_loader
from app.config import settings
from app_logging.event_logger import log_event


def run_inference(faces: List[np.ndarray]) -> List[float]:
    """
    Runs deepfake inference on aligned face crops.

    Args:
        faces: List of face images (RGB, normalized, HxWx3)

    Returns:
        List of deepfake probabilities per face
    """

    if len(faces) == 0:
        return []

    loader = get_model_loader()
    model = loader.get_model()
    device = loader.get_device()

    # Convert to tensor: (N, C, H, W)
    face_tensor = torch.tensor(
        np.array(faces),
        dtype=torch.float32
    ).permute(0, 3, 1, 2)

    face_tensor = face_tensor.to(device)

    if settings.USE_FP16:
        face_tensor = face_tensor.half()

    with torch.no_grad():
        outputs = model(face_tensor)

        # Assumption: model outputs logits or probabilities
        if outputs.dim() > 1 and outputs.size(1) > 1:
            probs = torch.softmax(outputs, dim=1)[:, 1]
        else:
            probs = torch.sigmoid(outputs).squeeze()

    predictions = probs.detach().cpu().numpy().tolist()

    log_event(
        "INFERENCE_COMPLETE",
        {
            "faces_processed": len(faces),
            "avg_score": float(np.mean(predictions))
        }
    )

    return predictions
