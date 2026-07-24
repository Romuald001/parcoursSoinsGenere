from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from app.domain.models.enums import AlertSeverity


class Alert(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    severity: AlertSeverity
    message: str
    triggered_by: str | None = Field(
        default=None,
        description="Cause de l'alerte (ex: 'interaction médicamenteuse détectée'). "
                    "Obligatoire pour les alertes critiques (traçabilité/explicabilité)."
    )

    @model_validator(mode="after")
    def check_critical_alert_has_cause(self) -> "Alert":
        """Traduit la contrainte OCL :
        severity = 'critical' implies triggered_by is not null"""
        if self.severity == AlertSeverity.CRITICAL and not self.triggered_by:
            raise ValueError("Une alerte critique doit obligatoirement préciser 'triggered_by' (explicabilité).")
        return self