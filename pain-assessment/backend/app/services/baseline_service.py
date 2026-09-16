import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, status

from app.db.supabase_client import supabase
from app.schemas.baseline import BaselineObservationCreate


def is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def resolve_patient_uuid(patient_id_or_code: str) -> str:
    if is_valid_uuid(patient_id_or_code):
        return str(patient_id_or_code)

    response = (
        supabase
        .table("patients")
        .select("id")
        .eq("patient_code", patient_id_or_code)
        .maybe_single()
        .execute()
    )

    if not response or not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{patient_id_or_code}' not found",
        )

    return response.data["id"]


def add_baseline_observation(
    observation: BaselineObservationCreate,
):
    observation_data = observation.model_dump(
        exclude_none=True,
        mode="json",
    )
    observation_data["patient_id"] = resolve_patient_uuid(str(observation.patient_id))

    response = (
        supabase
        .table("baseline_observations")
        .insert(observation_data)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Baseline observation could not be stored",
        )

    return response.data[0]


def get_baseline_observations(patient_id_or_code: str):
    patient_uuid = resolve_patient_uuid(patient_id_or_code)
    response = (
        supabase
        .table("baseline_observations")
        .select("*")
        .eq("patient_id", patient_uuid)
        .order("observed_at")
        .execute()
    )

    return response.data


def calculate_baseline(
    patient_id_or_code: str,
    modality: str,
    feature_name: str,
):
    patient_uuid = resolve_patient_uuid(patient_id_or_code)
    observations_response = (
        supabase
        .table("baseline_observations")
        .select("feature_value, observed_at")
        .eq("patient_id", patient_uuid)
        .eq("modality", modality)
        .eq("feature_name", feature_name)
        .order("observed_at")
        .execute()
    )

    observations = observations_response.data

    if not observations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No baseline observations found",
        )

    values = [
        float(item["feature_value"])
        for item in observations
    ]

    count = len(values)
    mean_value = sum(values) / count

    sorted_values = sorted(values)
    middle = count // 2

    if count % 2 == 0:
        median_value = (
            sorted_values[middle - 1]
            + sorted_values[middle]
        ) / 2
    else:
        median_value = sorted_values[middle]

    minimum = min(values)
    maximum = max(values)

    variance = sum(
        (value - mean_value) ** 2
        for value in values
    ) / count

    stddev = variance ** 0.5

    baseline_data = {
        "patient_id": patient_uuid,
        "modality": modality,
        "feature_name": feature_name,
        "baseline_mean": mean_value,
        "baseline_median": median_value,
        "baseline_min": minimum,
        "baseline_max": maximum,
        "baseline_stddev": stddev,
        "sample_count": count,
        "baseline_start": observations[0]["observed_at"],
        "baseline_end": observations[-1]["observed_at"],
        "is_active": True,
        "updated_at": datetime.now(
            timezone.utc,
        ).isoformat(),
    }

    response = (
        supabase
        .table("patient_baselines")
        .upsert(
            baseline_data,
            on_conflict="patient_id,modality,feature_name",
        )
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Baseline could not be calculated",
        )

    return response.data[0]


def get_patient_baselines(patient_id_or_code: str):
    patient_uuid = resolve_patient_uuid(patient_id_or_code)
    response = (
        supabase
        .table("patient_baselines")
        .select("*")
        .eq("patient_id", patient_uuid)
        .eq("is_active", True)
        .order("modality")
        .execute()
    )

    return response.data


def calculate_deviation(
    patient_id_or_code: str,
    modality: str,
    feature_name: str,
    current_value: float,
):
    patient_uuid = resolve_patient_uuid(patient_id_or_code)
    baseline_response = (
        supabase
        .table("patient_baselines")
        .select("*")
        .eq("patient_id", patient_uuid)
        .eq("modality", modality)
        .eq("feature_name", feature_name)
        .eq("is_active", True)
        .maybe_single()
        .execute()
    )

    baseline = baseline_response.data

    if not baseline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baseline not found for this feature",
        )

    baseline_mean = baseline["baseline_mean"]

    if baseline_mean is None:
        deviation = None
        deviation_percentage = None
    else:
        deviation = current_value - float(baseline_mean)

        if float(baseline_mean) != 0:
            deviation_percentage = (
                deviation / float(baseline_mean)
            ) * 100
        else:
            deviation_percentage = None

    return {
        "patient_id": patient_uuid,
        "modality": modality,
        "feature_name": feature_name,
        "baseline_mean": baseline_mean,
        "current_value": current_value,
        "deviation": deviation,
        "deviation_percentage": deviation_percentage,
    }


def get_patient_voice_baseline(
    patient_id: str,
) -> dict[str, dict[str, Any]]:
    """
    Retrieve active voice baseline features for a patient.
    """
    patient_uuid = resolve_patient_uuid(patient_id)

    response = (
        supabase
        .table("patient_baselines")
        .select("*")
        .eq("patient_id", patient_uuid)
        .eq("modality", "voice")
        .eq("is_active", True)
        .execute()
    )

    baseline_features: dict[
        str,
        dict[str, Any],
    ] = {}

    for row in response.data or []:
        feature_name = row.get(
            "feature_name"
        )

        if feature_name:
            baseline_features[feature_name] = {
                "baseline_mean": row.get(
                    "baseline_mean"
                ),
                "baseline_stddev": row.get(
                    "baseline_stddev"
                ),
                "baseline_min": row.get(
                    "baseline_min"
                ),
                "baseline_max": row.get(
                    "baseline_max"
                ),
                "sample_count": row.get(
                    "sample_count"
                ),
            }

    return baseline_features

