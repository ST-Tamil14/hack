import uuid
from typing import List
from fastapi import HTTPException, status

from app.db.supabase_client import supabase
from app.schemas.kpi import KPICreate, KPIUpdate


FEATURE_MODALITY_MAP = {
    # Facial
    "brow_contraction": "facial",
    "eye_closure": "facial",
    "jaw_tension": "facial",
    "lip_compression": "facial",
    "grimacing": "facial",
    "facial_asymmetry": "facial",
    "facial_tension": "facial",
    "facial_activity": "facial",

    # Physiological
    "heart_rate": "physiological",
    "heart_rate_deviation": "physiological",
    "respiratory_rate": "physiological",
    "respiratory_variability": "physiological",
    "breathing_irregularity": "physiological",
    "eda_gsr": "physiological",
    "spo2": "physiological",
    "skin_temperature": "physiological",
    "perfusion_index": "physiological",
    "hrv": "physiological",

    # Behavioral
    "guarding": "behavioral",
    "withdrawal": "behavioral",
    "protective_movement": "behavioral",
    "movement_frequency": "behavioral",
    "gait_asymmetry": "behavioral",
    "movement_speed": "behavioral",
    "range_of_motion": "behavioral",
    "movement_smoothness": "behavioral",

    # Voice
    "pitch_variation": "voice",
    "vocal_intensity": "voice",
    "speech_rate": "voice",
    "pause_duration": "voice",
    "vocal_strain": "voice",
    "moaning": "voice",
    "groaning": "voice",
    "vocal_distress": "voice",
}


def derive_required_modalities(selected_features: List[str]) -> List[str]:
    modalities = set()
    for feature in selected_features:
        modality = FEATURE_MODALITY_MAP.get(feature)
        if modality:
            modalities.add(modality)
    return sorted(list(modalities))


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


def get_kpi_catalog():
    response = (
        supabase
        .table("kpi_catalog")
        .select("*")
        .order("kpi_category")
        .execute()
    )

    return response.data


def get_kpi_catalog_by_category(category: str):
    response = (
        supabase
        .table("kpi_catalog")
        .select("*")
        .eq("kpi_category", category)
        .execute()
    )

    return response.data


def create_kpi(kpi: KPICreate):
    kpi_data = kpi.model_dump(
        exclude_none=True,
        mode="json",
    )

    kpi_data["patient_id"] = resolve_patient_uuid(str(kpi.patient_id))

    # Auto-derive modalities if not provided or to ensure full coverage
    derived = derive_required_modalities(kpi.selected_features)
    if derived:
        combined_modalities = sorted(list(set(kpi.required_modalities).union(set(derived))))
        kpi_data["required_modalities"] = combined_modalities

    response = (
        supabase
        .table("kpi_configs")
        .insert(kpi_data)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="KPI could not be created",
        )

    return response.data[0]


def get_patient_kpis(patient_id_or_code: str, active_only: bool = True):
    patient_uuid = resolve_patient_uuid(patient_id_or_code)
    query = (
        supabase
        .table("kpi_configs")
        .select("*")
        .eq("patient_id", patient_uuid)
    )
    if active_only:
        query = query.eq("is_active", True)
    response = query.order("created_at").execute()

    return response.data


def get_kpi_by_id(kpi_id: str):
    response = (
        supabase
        .table("kpi_configs")
        .select("*")
        .eq("id", kpi_id)
        .maybe_single()
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI not found",
        )

    return response.data


def update_kpi(kpi_id: str, kpi: KPIUpdate):
    update_data = kpi.model_dump(
        exclude_none=True,
        mode="json",
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update fields were provided",
        )

    # Re-derive modalities if selected_features are updated
    if "selected_features" in update_data:
        derived = derive_required_modalities(update_data["selected_features"])
        if derived:
            existing_modalities = update_data.get("required_modalities", [])
            combined_modalities = sorted(list(set(existing_modalities).union(set(derived))))
            update_data["required_modalities"] = combined_modalities

    response = (
        supabase
        .table("kpi_configs")
        .update(update_data)
        .eq("id", kpi_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI not found or could not be updated",
        )

    return response.data[0]


def deactivate_kpi(kpi_id: str):
    response = (
        supabase
        .table("kpi_configs")
        .update({"is_active": False})
        .eq("id", kpi_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KPI not found",
        )

    return {
        "message": "KPI deactivated successfully",
        "kpi_id": kpi_id,
    }
