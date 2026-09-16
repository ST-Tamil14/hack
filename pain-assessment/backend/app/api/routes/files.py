from typing import List

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.auth import require_roles
from app.schemas.file import MultimodalFileResponse
from app.services.audit_service import create_audit_log
from app.services.storage_service import (
    get_file_download_url,
    get_patient_files,
    upload_multimodal_file,
)


router = APIRouter(
    prefix="/files",
    tags=["Multimodal Files"],
)


@router.post(
    "/upload/{patient_id}",
    response_model=MultimodalFileResponse,
    summary="Upload a multimodal file for a patient by UUID or patient code",
)
def upload_file_endpoint(
    patient_id: str,
    modality: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher")),
):
    result = upload_multimodal_file(
        patient_id_or_code=patient_id,
        modality=modality,
        file=file,
    )
    file_id = result.get("id") if isinstance(result, dict) else str(getattr(result, "id", ""))
    p_id = result.get("patient_id") if isinstance(result, dict) else patient_id

    create_audit_log(
        user_id=current_user["id"],
        action="FILE_UPLOADED",
        resource_type="file",
        resource_id=str(file_id) if file_id else None,
        patient_id=str(p_id) if p_id else None,
    )

    return result


@router.get(
    "/patient/{patient_id}",
    response_model=List[MultimodalFileResponse],
    summary="Get all uploaded files for a patient by UUID or patient code",
)
def get_patient_files_endpoint(
    patient_id: str,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return get_patient_files(patient_id)


@router.get(
    "/download-url",
    summary="Generate a temporary signed download URL for a file",
)
def get_download_url_endpoint(
    storage_path: str,
    expires_in: int = 300,
    current_user: dict = Depends(require_roles("admin", "doctor", "nurse", "researcher", "viewer")),
):
    return get_file_download_url(storage_path, expires_in)
