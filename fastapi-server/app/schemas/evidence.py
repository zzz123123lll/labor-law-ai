from pydantic import BaseModel


class EvidenceUploadResponse(BaseModel):
    id: str
    file_url: str
    file_type: str
    ocr_text: str | None
    created_at: str

    class Config:
        from_attributes = True


class EvidenceListResponse(BaseModel):
    id: str
    file_url: str
    file_type: str
    ocr_text: str | None
    analysis: dict | None
    created_at: str

    class Config:
        from_attributes = True
