from fastapi import APIRouter, BackgroundTasks, status

from app.schemas.processing_job import (
    ProcessingJobCreate,
    ProcessingJobResponse,
    ProcessingJobStatusUpdate,
)
from app.services.processing_job_service import (
    create_processing_job,
    get_processing_job,
    list_patient_processing_jobs,
    update_processing_job,
)


router = APIRouter(
    prefix="/processing/jobs",
    tags=["Processing Jobs"],
)


def placeholder_processor(job_id: str) -> None:
    """
    Temporary placeholder.

    This does not run real AI processing yet.
    It only demonstrates the processing lifecycle.
    """

    try:
        update_processing_job(
            job_id=job_id,
            status="processing",
            progress=10,
        )

        # Real AI processing will be added later.
        #
        # Example:
        # 1. Download file from Supabase Storage
        # 2. Preprocess the file
        # 3. Extract features
        # 4. Run the appropriate AI model
        # 5. Save the result
        # 6. Update the job as processed

        update_processing_job(
            job_id=job_id,
            status="processed",
            progress=100,
        )

    except Exception as exc:
        update_processing_job(
            job_id=job_id,
            status="failed",
            progress=0,
            error_message=str(exc),
        )


@router.post(
    "/{file_id}",
    response_model=ProcessingJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    file_id: str,
    background_tasks: BackgroundTasks,
):
    job = create_processing_job(file_id)

    background_tasks.add_task(
        placeholder_processor,
        job["id"],
    )

    return job


@router.get(
    "/{job_id}",
    response_model=ProcessingJobResponse,
)
def get_job(job_id: str):
    return get_processing_job(job_id)


@router.get(
    "/patient/{patient_id}",
    response_model=list[ProcessingJobResponse],
    summary="List processing jobs for a patient by UUID or patient code",
)
def get_patient_jobs(patient_id: str):
    return list_patient_processing_jobs(patient_id)


@router.patch(
    "/{job_id}/status",
    response_model=ProcessingJobResponse,
)
def update_job_status(
    job_id: str,
    payload: ProcessingJobStatusUpdate,
):
    return update_processing_job(
        job_id=job_id,
        status=payload.status,
        progress=payload.progress,
        error_message=payload.error_message,
        result_path=payload.result_path,
    )
