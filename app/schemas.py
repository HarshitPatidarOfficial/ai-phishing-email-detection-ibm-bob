from pydantic import BaseModel, Field, field_validator


class EmailRequest(BaseModel):
    sender: str = Field(default="", max_length=320)
    subject: str = Field(default="", max_length=500)
    body: str = Field(min_length=1, max_length=20000)

    @field_validator("sender", "subject", "body")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class EmailPrediction(BaseModel):
    label: str
    risk_score: float
    confidence: float
    indicators: list[str]
    recommendation: str
    model_version: str
