from fastapi import APIRouter, BackgroundTasks

from app.services.preprocessing_service import (
    preprocess_file,
)


router = APIRouter(
    prefix="/preprocessing",
    tags=["Preprocessing"],
)


def run_preprocessing(file_id: str) -> None:
    try:
        preprocess_file(file_id)
    except Exception as exc:
        print(
            f"Preprocessing failed for file "
            f"{file_id}: {exc}"
        )


@router.post("/files/{file_id}")
def start_preprocessing(
    file_id: str,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(
        run_preprocessing,
        file_id,
    )

    return {
        "message": "Preprocessing started",
        "file_id": file_id,
        "status": "processing",
    }
