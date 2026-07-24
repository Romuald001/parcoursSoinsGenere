from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.models.symptom import Symptom


class Diagnostic(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    label: str
    icd10_code: str | None = Field(
        default=None,
        description="Code CIM-10 si identifiable, pour rattachement à une nomenclature standard."
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    symptoms: list[Symptom] = Field(default_factory=list)