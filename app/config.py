import os
from pathlib import Path


class Settings:
    """
    Central configuration object for the entire Edge AI system.
    Loaded once and imported everywhere.
    """
   
    # =========================
    # Runtime Mode
    # =========================
    ENV = os.getenv("ENV", "local")  # local | staging | production
    DEBUG = ENV == "local"
    RUNTIME_MODE = "EDGE_OFFLINE"

    # =========================
    # Server
    # =========================
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 8000))

    # =========================
    # Paths
    # =========================
    BASE_DIR = Path(__file__).resolve().parent.parent
    MODEL_DIR = BASE_DIR / "models"
    DATA_DIR = BASE_DIR / "data"
    LOG_DIR = BASE_DIR / "app_logging"

    # =========================
    # Model Configuration (Video Only)
    # =========================
    DEEPFAKE_MODEL_PATH = MODEL_DIR / "deepfake_model.pth"
    MODEL_METADATA_PATH = MODEL_DIR / "model_metadata.json"

    # =========================
    # Audio Configuration (Heuristic-based)
    # =========================
    # Audio detection now uses signal processing (no model needed)
    SAMPLE_RATE = 16000
    
    # Heuristic detection thresholds (can be tuned)
    AUDIO_DEEPFAKE_THRESHOLD_HIGH = 0.70  # >70% = likely fake
    AUDIO_DEEPFAKE_THRESHOLD_LOW = 0.30   # <30% = likely real

    # =========================
    # Device Configuration
    # =========================
    DEVICE = "cpu"  # auto-detection can be added later
    USE_FP16 = False

    # =========================
    # Inference Thresholds (Video)
    # =========================
    # These directly affect the agent's decision logic
    DEEPFAKE_THRESHOLD_HIGH = 0.75
    DEEPFAKE_THRESHOLD_LOW = 0.40

    # =========================
    # Preprocessing
    # =========================
    FRAME_SAMPLE_RATE = 10          # frames per second
    MAX_FRAMES = 150               # hard cap for edge safety
    FACE_IMAGE_SIZE = 224

    # =========================
    # Security
    # =========================
    ENABLE_INTEGRITY_CHECK = True
    ALLOW_EXTERNAL_NETWORK = False

    # =========================
    # Logging
    # =========================
    ENABLE_EVENT_LOGGING = True
    LOG_LEVEL = "INFO"

    # =========================
    # Future Expansion Flags
    # =========================
    ENABLE_FEDERATED = False
    ENABLE_RBAC = False


# Singleton-style access
settings = Settings()