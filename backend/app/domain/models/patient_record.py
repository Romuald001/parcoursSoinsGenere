from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.models.patient import Patient
from app.domain.models.diagnostic import Diagnostic
from app.domain.models.medication import Medication
from app.domain.models.treatment_step import TreatmentStep
from app.domain.models.clinical_goal import ClinicalGoal
from app.domain.models.alert import Alert
from app.domain.models.appointment import Appointment


class PatientRecord(BaseModel):
    """Objet racine du pipeline : agrège le patient et l'ensemble
    de son parcours de soins généré à partir des notes du médecin.

    C'est le contrat d'échange entre tous les agents SMA :
    - sortie de l'Agent Extracteur (état initial, confidences brutes)
    - entrée/sortie de l'Agent Vérificateur (peut ajouter des Alerts)
    - entrée/sortie de l'Agent Personnalisateur (peut réordonner/simplifier)
    - entrée de la transformation M2T (génère le schéma UI final)
    """

    id: UUID = Field(default_factory=uuid4)
    patient: Patient
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    medications: list[Medication] = Field(default_factory=list)
    treatment_steps: list[TreatmentStep] = Field(default_factory=list)
    clinical_goals: list[ClinicalGoal] = Field(default_factory=list)
    alerts: list[Alert] = Field(default_factory=list)
    appointments: list[Appointment] = Field(default_factory=list)

    def add_alert(self, alert: Alert) -> None:
        """Point d'entrée unique pour ajouter une alerte (utilisé par l'Agent Vérificateur)."""
        self.alerts.append(alert)

    def low_confidence_items(self, threshold: float = 0.6) -> dict[str, list]:
        """Retourne tous les éléments dont la confidence est sous le seuil.
        Utile pour l'Agent Vérificateur : identifier ce qui mérite une alerte
        ou une intervention humaine avant publication."""
        return {
            "diagnostics": [d for d in self.diagnostics if d.confidence < threshold],
            "medications": [m for m in self.medications if m.confidence < threshold],
            "symptoms": [
                s for d in self.diagnostics for s in d.symptoms if s.confidence < threshold
            ],
        }