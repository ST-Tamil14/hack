from fastapi import APIRouter

from app.schemas.feature import FeatureExtractionResponse
from app.services.feature_extraction_service import (
    extract_features,
)


router = APIRouter(
    prefix="/features",
    tags=["Feature Extraction"],
)


@router.post(
    "/extract/{file_id}/{processing_job_id}",
    response_model=FeatureExtractionResponse,
)
def extract_file_features(
    file_id: str,
    processing_job_id: str,
):
    return extract_features(
        file_id=file_id,
        processing_job_id=processing_job_id,
    )
