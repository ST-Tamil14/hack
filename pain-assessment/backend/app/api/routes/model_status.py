from pathlib import Path

from fastapi import APIRouter


router = APIRouter(
    prefix="/models",
    tags=["Model Status"],
)


PROJECT_ROOT = (
    Path(__file__).resolve().parents[3]
)

FACIAL_MODEL_PATH = PROJECT_ROOT / "models" / "facial_cnn_lstm_best.pt"
FACIAL_SCALER_PATH = PROJECT_ROOT / "datasets" / "processed" / "facial" / "real_facial_scaler.npz"

PHYSIOLOGICAL_MODEL_PATH = PROJECT_ROOT / "models" / "physiological_cnn_lstm_best.pt"
PHYSIOLOGICAL_SCALER_PATH = PROJECT_ROOT / "datasets" / "processed" / "physiological" / "physiological_scaler.npz"

BEHAVIORAL_MODEL_PATH = PROJECT_ROOT / "models" / "behavioral_cnn_lstm_best.pt"
BEHAVIORAL_SCALER_PATH = PROJECT_ROOT / "datasets" / "processed" / "behavioral" / "behavioral_scaler.npz"

VOICE_MODEL_PATH = PROJECT_ROOT / "models" / "voice_cnn_lstm_best.pt"
VOICE_SCALER_PATH = PROJECT_ROOT / "datasets" / "processed" / "voice" / "voice_scaler.npz"

FUSION_MODEL_PATH = PROJECT_ROOT / "models" / "multimodal_fusion_best.pt"
FUSION_SCALER_PATH = PROJECT_ROOT / "datasets" / "processed" / "fusion" / "fusion_scaler.npz"

FACIAL_ARCH_PATH = PROJECT_ROOT / "app" / "ml" / "facial_model.py"
PHYSIO_ARCH_PATH = PROJECT_ROOT / "app" / "ml" / "physiological_model.py"
BEHAVIORAL_ARCH_PATH = PROJECT_ROOT / "app" / "ml" / "behavioral_model.py"
VOICE_ARCH_PATH = PROJECT_ROOT / "app" / "ml" / "voice_model.py"
FUSION_ARCH_PATH = PROJECT_ROOT / "app" / "ml" / "fusion_model.py"


@router.get("/status")
def get_model_status():
    facial_arch = FACIAL_ARCH_PATH.exists()
    facial_ckpt = FACIAL_MODEL_PATH.exists()
    facial_scaler = FACIAL_SCALER_PATH.exists()
    facial_ready = facial_arch and facial_ckpt and facial_scaler

    physio_arch = PHYSIO_ARCH_PATH.exists()
    physio_ckpt = PHYSIOLOGICAL_MODEL_PATH.exists()
    physio_scaler = PHYSIOLOGICAL_SCALER_PATH.exists()
    physio_ready = physio_arch and physio_ckpt and physio_scaler

    behavioral_arch = BEHAVIORAL_ARCH_PATH.exists()
    behavioral_ckpt = BEHAVIORAL_MODEL_PATH.exists()
    behavioral_scaler = BEHAVIORAL_SCALER_PATH.exists()
    behavioral_ready = behavioral_arch and behavioral_ckpt and behavioral_scaler

    voice_arch = VOICE_ARCH_PATH.exists()
    voice_ckpt = VOICE_MODEL_PATH.exists()
    voice_scaler = VOICE_SCALER_PATH.exists()
    voice_ready = voice_arch and voice_ckpt and voice_scaler

    fusion_arch = FUSION_ARCH_PATH.exists()
    fusion_ckpt = FUSION_MODEL_PATH.exists()
    fusion_scaler = FUSION_SCALER_PATH.exists()
    fusion_ready = fusion_arch and fusion_ckpt and fusion_scaler

    models_status = {
        "facial": {
            "architecture_available": facial_arch,
            "checkpoint_available": facial_ckpt,
            "scaler_available": facial_scaler,
            "status": "ready" if facial_ready else "not_ready",
            "model_name": "facial_cnn_lstm",
            "model_version": "facial-cnn-lstm-v1",
        },
        "physiological": {
            "architecture_available": physio_arch,
            "checkpoint_available": physio_ckpt,
            "scaler_available": physio_scaler,
            "status": "ready" if physio_ready else "not_ready",
            "model_name": "physiological_cnn_lstm",
            "model_version": "physiological-cnn-lstm-v1",
        },
        "behavioral": {
            "architecture_available": behavioral_arch,
            "checkpoint_available": behavioral_ckpt,
            "scaler_available": behavioral_scaler,
            "status": "ready" if behavioral_ready else "not_ready",
            "model_name": "behavioral_cnn_lstm",
            "model_version": "behavioral-cnn-lstm-v1",
        },
        "voice": {
            "architecture_available": voice_arch,
            "checkpoint_available": voice_ckpt,
            "scaler_available": voice_scaler,
            "status": "ready" if voice_ready else "not_ready",
            "model_name": "voice_cnn_lstm",
            "model_version": "voice-cnn-lstm-v1",
        },
        "fusion": {
            "architecture_available": fusion_arch,
            "checkpoint_available": fusion_ckpt,
            "scaler_available": fusion_scaler,
            "status": "ready" if fusion_ready else "not_ready",
            "model_name": "multimodal_fusion_mlp",
            "model_version": "multimodal-fusion-v1",
        },
    }

    return {
        "models": models_status,
        "facial": models_status["facial"],
        "physiological": models_status["physiological"],
        "behavioral": models_status["behavioral"],
        "voice": models_status["voice"],
        "fusion": models_status["fusion"],
    }
