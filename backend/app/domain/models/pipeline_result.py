from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.models.patient_record import PatientRecord
from app.domain.models.personalized_summary import PersonalizedSummary


class PipelineResult(BaseModel):
    """Résultat consolidé de l'exécution complète du pipeline SMA.
    Objet transmis à la transformation M2T pour générer le schéma UI final."""

    id: UUID = Field(default_factory=uuid4)
    patient_record: PatientRecord
    personalized_summary: PersonalizedSummary