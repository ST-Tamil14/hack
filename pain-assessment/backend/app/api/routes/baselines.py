from typing import List

from fastapi import APIRouter, Depends, status

from app.core.auth import require_roles
from app.schemas.baseline import (
    BaselineDeviationResponse,
    BaselineObservationCreate,
    BaselineResponse,
)
from app.services.baseline_service import (
    add_baseline_observation,
    calculate_baseline,
    calculate_deviation,
    get_baseline_observations,
    get_patient_baselines,
)


router = APIRouter(
    prefix="/baselines",
    tags=["Baselines"],
)


@router.post(
    "/observations",
    status_code=status.HTTP_201_CREATED,
)
def add_baseline_observation_endpoint(
    observation: BaselineObservationCreate,
    current_user: dict = Depends(require_roles("admin", "doctor", "researcher")),
):
    return add_baseline_observation(observation)


@router.get(
    "/observations/patient/{patient_id}",
    summary="Get baseline observations by patient UUID or patient code",
)
def get_baseline_observations_endpoint(
    patient_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return get_baseline_observations(patient_id)


@router.post(
    "/calculate/{patient_id}/{modality}/{feature_name}",
    response_model=BaselineResponse,
    summary="Calculate baseline for a patient feature by UUID or patient code",
)
def calculate_baseline_endpoint(
    patient_id: str,
    modality: str,
    feature_name: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "researcher")),
):
    return calculate_baseline(
        patient_id,
        modality,
        feature_name,
    )


@router.get(
    "/patient/{patient_id}",
    response_model=List[BaselineResponse],
    summary="Get patient baselines by UUID or patient code",
)
def get_patient_baselines_endpoint(
    patient_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return get_patient_baselines(patient_id)


@router.get(
    "/deviation/{patient_id}/{modality}/{feature_name}",
    response_model=BaselineDeviationResponse,
    summary="Calculate current value deviation from baseline by UUID or patient code",
)
def calculate_deviation_endpoint(
    patient_id: str,
    modality: str,
    feature_name: str,
    current_value: float,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return calculate_deviation(
        patient_id,
        modality,
        feature_name,
        current_value,
    )
