from datetime import date
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class Medication(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    dosage: str
    frequency: str
    start_date: date | None = None
    end_date: date | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def check_dates_order(self) -> "Medication":
        """Traduit la contrainte OCL : end_date is null or end_date >= start_date"""
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError(
                f"end_date ({self.end_date}) ne peut pas être antérieure "
                f"à start_date ({self.start_date})"
            )
        return self