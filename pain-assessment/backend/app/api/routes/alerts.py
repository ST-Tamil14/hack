from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import require_roles
from app.schemas.alert import ClinicianFeedbackCreate
from app.services.alert_state_service import (
    acknowledge_alert,
    calculate_false_alarm_metrics,
    get_active_alerts,
    get_calibration_records,
    get_patient_alerts,
    resolve_alert,
    submit_clinician_feedback,
)

router = APIRouter(
    prefix="/alerts",
    tags=["Monitoring Alerts"],
)


@router.get("/patient/{patient_id}")
def list_patient_alerts(
    patient_id: str,
    current_user: dict = Depends(
        require_roles("admin", "doctor", "nurse", "researcher", "viewer")
    ),
):
    """Retrieves all monitoring alerts recorded for a specific patient."""
    return get_patient_alerts(patient_id)


@router.get("/active")
def list_active_alerts(
    current_user: dict = Depends(
        require_roles("admin", "doctor", "nurse", "researcher", "viewer")
    ),
):
    """Retrieves all open or acknowledged alerts requiring clinician attention."""
    return get_active_alerts()


@router.post("/{alert_id}/acknowledge")
def acknowledge_alert_endpoint(
    alert_id: str,
    current_user: dict = Depends(
        require_roles("admin", "doctor", "nurse")
    ),
):
    """Marks a monitoring alert as acknowledged by the active clinician."""
    user_id = current_user.get("id", "current_user")
    return acknowledge_alert(alert_id, user_id=user_id)


@router.post("/{alert_id}/resolve")
def resolve_alert_endpoint(
    alert_id: str,
    current_user: dict = Depends(
        require_roles("admin", "doctor", "nurse")
    ),
):
    """Marks a monitoring alert as resolved."""
    user_id = current_user.get("id", "current_user")
    return resolve_alert(alert_id, user_id=user_id)


@router.post("/{alert_id}/feedback")
def submit_feedback_endpoint(
    alert_id: str,
    feedback: ClinicianFeedbackCreate,
    current_user: dict = Depends(
        require_roles("admin", "doctor", "nurse")
    ),
):
    """Submits clinician feedback (true_positive, false_positive, etc.) for false-alarm analysis."""
    return submit_clinician_feedback(
        alert_id=alert_id,
        clinician_label=feedback.clinician_label,
        clinician_feedback=feedback.clinician_feedback,
    )


@router.get("/metrics/performance")
def get_performance_metrics(
    patient_id: Optional[str] = Query(default=None),
    current_user: dict = Depends(
        require_roles("admin", "doctor", "nurse", "researcher", "viewer")
    ),
):
    """Calculates false-alarm rate, missed episode rate, positive predictive value,

    alert confirmation rate, and calibration parameters.
    """
    return calculate_false_alarm_metrics(patient_id=patient_id)


@router.get("/calibrations")
def get_calibrations_endpoint(
    current_user: dict = Depends(
        require_roles("admin", "doctor", "nurse", "researcher", "viewer")
    ),
):
    """Retrieves model calibration records and metrics (ECE, Brier score, temperature scaling)."""
    return get_calibration_records()
