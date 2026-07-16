from pydantic import BaseModel, ConfigDict


class DocumentGenerateRequest(BaseModel):
    case_id: str
    doc_type: str  # arbitration_request | complaint_letter | evidence_list


class DocumentResponse(BaseModel):
    id: str
    doc_type: str
    title: str
    content: str
    status: str
    created_at: str

    model_config = ConfigDict(
        from_attributes=True)
