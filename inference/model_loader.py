import sys
import os
import json
import torch
from pathlib import Path
# Add the project root to path so 'import model' works
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import settings
from app_logging.event_logger import log_event


class ModelLoader:
    """
    Centralized deepfake model loader for Video (Xception).
    Audio detection now uses heuristic methods (no model needed).

    Responsibilities:
    - Load PyTorch model for video
    - Handle device placement
    - Set eval mode
    """

    def __init__(self):
        self.device = torch.device(settings.DEVICE)
        
        # Video Model state
        self.video_model = None
        self.video_metadata = None

        # Load video pipeline
        self._load_video_pipeline()

    def _load_video_pipeline(self):
        """Loads the Xception video deepfake model and metadata."""
        metadata_path = Path(settings.MODEL_METADATA_PATH)
        model_path = Path(settings.DEEPFAKE_MODEL_PATH)

        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                self.video_metadata = json.load(f)
            
        if model_path.exists():
            self.video_model = torch.load(model_path, map_location=self.device, weights_only=False)
            self.video_model.to(self.device)
            self.video_model.eval()
            log_event("VIDEO_MODEL_LOADED", {"model": self.video_metadata.get("model_name")})

    def get_model(self):
        """Returns the video model."""
        return self.video_model

    def get_device(self):
        return self.device


# Singleton-style access
_model_loader = None


def get_model_loader():
    global _model_loader
    if _model_loader is None:
        _model_loader = ModelLoader()
    return _model_loader