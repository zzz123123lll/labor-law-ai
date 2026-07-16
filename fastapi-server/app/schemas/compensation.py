from pydantic import BaseModel, ConfigDict


class CompensationRequest(BaseModel):
    case_id: str


class CompensationResponse(BaseModel):
    id: str
    items: list
    total_min: float
    total_max: float
    calculation: str | None
    created_at: str

    model_config = ConfigDict(
        from_attributes=True)
