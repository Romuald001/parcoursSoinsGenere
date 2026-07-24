from datetime import date
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.models.enums import Severity


class Symptom(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    label: str
    severity: Severity
    onset_date: date | None = None
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0,
        description="Score de confiance de l'extraction LLM (1.0 = extrait explicitement du texte)."
    )