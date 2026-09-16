from pydantic import BaseModel, Field


class DatasetRecord(BaseModel):
    sample_id: str
    patient_id: str

    file_path: str

    label: int | float | str

    split: str | None = None

    metadata: dict = Field(
        default_factory=dict
    )
