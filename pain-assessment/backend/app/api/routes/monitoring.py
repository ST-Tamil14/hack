from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_roles
from app.schemas.monitoring import (
    MonitoringResponse,
)
from app.services.monitoring_service import (
    get_patient_monitoring,
)


router = APIRouter(
    prefix="/monitoring",
    tags=["Patient Monitoring"],
)


@router.get(
    "/patient/{patient_id}",
    response_model=MonitoringResponse,
)
def patient_monitoring(
    patient_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    try:
        result = get_patient_monitoring(
            patient_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return result
