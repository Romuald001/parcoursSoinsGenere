from datetime import date
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from app.domain.models.enums import TreatmentStatus


class TreatmentStep(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    label: str
    status: TreatmentStatus = TreatmentStatus.PENDING
    scheduled_date: date | None = None
    related_diagnostic_id: UUID | None = None

    @model_validator(mode="after")
    def check_done_status_consistency(self) -> "TreatmentStep":
        """Traduit la contrainte OCL :
        status = 'done' implies scheduled_date <= today()"""
        if self.status == TreatmentStatus.DONE:
            if self.scheduled_date is None:
                raise ValueError("Une étape 'done' doit avoir une scheduled_date renseignée.")
            if self.scheduled_date > date.today():
                raise ValueError("Une étape 'done' ne peut pas avoir une date future.")
        return self