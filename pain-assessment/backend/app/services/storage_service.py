import uuid
from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException, UploadFile, status

from app.db.supabase_client import supabase


BUCKET_NAME = "clinical-data"


def download_storage_file(
    storage_path: str,
    temporary_directory: str = "temp",
) -> str:
    """
    Download a private Supabase Storage file locally.

    Returns:
        Local file path
    """
    temporary_dir = Path(temporary_directory)
    temporary_dir.mkdir(parents=True, exist_ok=True)

    filename = Path(storage_path).name
    local_filename = f"{uuid4()}_{filename}"
    local_path = temporary_dir / local_filename

    response = (
        supabase.storage
        .from_(BUCKET_NAME)
        .download(storage_path)
    )

    file_bytes = response if isinstance(response, bytes) else getattr(response, "content", response)
    local_path.write_bytes(file_bytes)

    return str(local_path)


ALLOWED_MODALITIES = {
    "facial",
    "behavioral",
    "voice",
    "physiological",
}

ALLOWED_CONTENT_TYPES = {
    "video/mp4",
    "video/webm",
    "audio/wav",
    "audio/mpeg",
    "audio/webm",
    "text/csv",
    "application/json",
    "application/octet-stream",
}

MAX_FILE_SIZE = 100 * 1024 * 1024


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


def upload_multimodal_file(
    patient_id_or_code: str,
    modality: str,
    file: UploadFile,
):
    if modality not in ALLOWED_MODALITIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported modality",
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type",
        )

    patient_uuid = resolve_patient_uuid(patient_id_or_code)
    file_content = file.file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 100 MB limit",
        )

    safe_filename = file.filename.replace(" ", "_") if file.filename else "file"
    unique_filename = f"{uuid4()}_{safe_filename}"

    storage_path = (
        f"{patient_uuid}/"
        f"{modality}/"
        f"{unique_filename}"
    )

    upload_response = (
        supabase
        .storage
        .from_("clinical-data")
        .upload(
            storage_path,
            file_content,
            {
                "content-type": file.content_type,
                "upsert": False,
            },
        )
    )

    if not upload_response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed",
        )

    metadata = {
        "patient_id": patient_uuid,
        "modality": modality,
        "file_type": file.content_type,
        "original_filename": file.filename or safe_filename,
        "storage_path": storage_path,
        "file_size_bytes": len(file_content),
        "content_type": file.content_type,
        "processing_status": "uploaded",
    }

    database_response = (
        supabase
        .table("multimodal_files")
        .insert(metadata)
        .execute()
    )

    if not database_response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File metadata could not be saved",
        )

    return database_response.data[0]


def get_patient_files(patient_id_or_code: str):
    patient_uuid = resolve_patient_uuid(patient_id_or_code)
    response = (
        supabase
        .table("multimodal_files")
        .select("*")
        .eq("patient_id", patient_uuid)
        .order("uploaded_at", desc=True)
        .execute()
    )

    return response.data


def get_file_download_url(
    storage_path: str,
    expires_in: int = 300,
):
    response = (
        supabase
        .storage
        .from_("clinical-data")
        .create_signed_url(
            storage_path,
            expires_in,
        )
    )

    return response


def create_signed_file_url(
    storage_path: str,
    expires_in: int = 300,
) -> str:
    response = (
        supabase.storage
        .from_("clinical-data")
        .create_signed_url(
            storage_path,
            expires_in,
        )
    )

    if isinstance(response, dict):
        return response.get("signedURL") or response.get("signedUrl", "")
    return getattr(response, "signed_url", str(response))

