from pydantic import BaseModel, ConfigDict


class EvidenceUploadResponse(BaseModel):
    id: str
    file_url: str
    file_type: str
    ocr_text: str | None
    created_at: str

    model_config = ConfigDict(
        from_attributes=True)


class EvidenceListResponse(BaseModel):
    id: str
    file_url: str
    file_type: str
    ocr_text: str | None
    analysis: dict | None
    created_at: str

    model_config = ConfigDict(
        from_attributes=True)
