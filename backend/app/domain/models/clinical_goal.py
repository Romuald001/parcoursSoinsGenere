from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class ClinicalGoal(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    label: str
    target_value: float | None = None
    current_value: float | None = None
    unit: str | None = None

    @model_validator(mode="after")
    def check_unit_required_with_values(self) -> "ClinicalGoal":
        """Traduit la contrainte OCL : une valeur numérique sans unité n'a pas de sens."""
        has_numeric_value = self.target_value is not None or self.current_value is not None
        if has_numeric_value and self.unit is None:
            raise ValueError("Une valeur numérique (target_value/current_value) nécessite une unité (unit).")
        return self