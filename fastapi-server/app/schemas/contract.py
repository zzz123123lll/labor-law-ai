from pydantic import BaseModel


class ContractReviewResponse(BaseModel):
    id: str
    score: int | None
    risk_level: str | None
    findings: list | None
    full_report: str | None
    created_at: str

    class Config:
        from_attributes = True
