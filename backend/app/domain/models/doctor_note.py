from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DoctorNote(BaseModel):
    """Note médicale en texte libre saisie par le médecin.
    C'est l'INPUT brut du pipeline (avant tout traitement par les agents)."""

    id: UUID = Field(default_factory=uuid4)
    patient_id: UUID
    raw_text: str = Field(
        ..., min_length=1,
        description="Texte libre rédigé par le médecin, non structuré."
    )
    created_at: datetime = Field(default_factory=datetime.now)