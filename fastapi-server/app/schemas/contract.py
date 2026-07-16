from pydantic import BaseModel, ConfigDict


class ContractReviewResponse(BaseModel):
    id: str
    score: int | None
    risk_level: str | None
    findings: list | None
    full_report: str | None
    created_at: str

    model_config = ConfigDict(
        from_attributes=True)
