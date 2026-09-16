from fastapi import APIRouter, Depends

from app.core.auth import require_roles
from app.schemas.voice_baseline import (
    VoiceBaselineComparisonRequest,
    VoiceBaselineComparisonResponse,
)
from app.services.voice_baseline_service import (
    compare_voice_with_baseline,
)


router = APIRouter(
    prefix="/voice-baselines",
    tags=["Voice Baselines"],
)


@router.post(
    "/compare",
    response_model=VoiceBaselineComparisonResponse,
)
def compare_voice_baseline(
    request: VoiceBaselineComparisonRequest,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    result = compare_voice_with_baseline(
        patient_id=request.patient_id,
        current_features=request.current_features,
    )

    return result
