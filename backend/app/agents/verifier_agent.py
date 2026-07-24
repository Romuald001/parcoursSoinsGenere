from app.agents.base import Agent
from app.domain.models.alert import Alert
from app.domain.models.enums import AlertSeverity
from app.domain.models.patient_record import PatientRecord


class VerifierAgent(Agent):
    """Agent Vérificateur : applique des règles métier déterministes
    (aucun appel LLM) sur un PatientRecord pour détecter incohérences
    et éléments à risque, et générer les Alert correspondantes."""

    LOW_CONFIDENCE_THRESHOLD = 0.6

    async def run(self, record: PatientRecord) -> PatientRecord:
        """Applique toutes les règles de vérification et enrichit
        le PatientRecord avec les Alert détectées. Retourne le même
        objet, modifié en place (et renvoyé pour chaînage explicite)."""
        self._check_low_confidence_items(record)
        self._check_vague_medications(record)
        self._check_achieved_goals_without_closure(record)
        return record

    def _check_low_confidence_items(self, record: PatientRecord) -> None:
        """R1 : signale tout élément dont la confiance est sous le seuil."""
        low_conf = record.low_confidence_items(threshold=self.LOW_CONFIDENCE_THRESHOLD)

        for diagnostic in low_conf["diagnostics"]:
            record.add_alert(Alert(
                severity=AlertSeverity.WARNING,
                message=f"Le diagnostic '{diagnostic.label}' a une confiance faible "
                        f"({diagnostic.confidence:.2f}) et mérite une vérification humaine.",
                triggered_by="low_confidence_diagnostic",
            ))

        for medication in low_conf["medications"]:
            record.add_alert(Alert(
                severity=AlertSeverity.WARNING,
                message=f"Le médicament '{medication.name}' a une confiance faible "
                        f"({medication.confidence:.2f}) et mérite une vérification humaine.",
                triggered_by="low_confidence_medication",
            ))

        for symptom in low_conf["symptoms"]:
            record.add_alert(Alert(
                severity=AlertSeverity.WARNING,
                message=f"Le symptôme '{symptom.label}' a une confiance faible "
                        f"({symptom.confidence:.2f}) et mérite une vérification humaine.",
                triggered_by="low_confidence_symptom",
            ))

    def _check_vague_medications(self, record: PatientRecord) -> None:
        """R3 : signale les médicaments avec une posologie manquante ou vide."""
        for medication in record.medications:
            if not medication.dosage.strip() or not medication.frequency.strip():
                record.add_alert(Alert(
                    severity=AlertSeverity.WARNING,
                    message=f"Le médicament '{medication.name}' a une posologie incomplète "
                            f"(dosage='{medication.dosage}', frequency='{medication.frequency}').",
                    triggered_by="incomplete_medication_dosage",
                ))

    def _check_achieved_goals_without_closure(self, record: PatientRecord) -> None:
        """R4 : signale un objectif clinique semblant atteint mais dont aucune
        étape de traitement liée n'est marquée 'done' (incohérence de suivi)."""
        done_diagnostic_ids = {
            step.related_diagnostic_id
            for step in record.treatment_steps
            if step.status.value == "done" and step.related_diagnostic_id is not None
        }

        for goal in record.clinical_goals:
            if goal.target_value is None or goal.current_value is None:
                continue

            goal_reached = goal.current_value <= goal.target_value

            if goal_reached and not done_diagnostic_ids:
                record.add_alert(Alert(
                    severity=AlertSeverity.INFO,
                    message=f"L'objectif '{goal.label}' semble atteint "
                            f"({goal.current_value}{goal.unit or ''} / cible "
                            f"{goal.target_value}{goal.unit or ''}) mais aucune étape "
                            f"de traitement n'est clôturée en conséquence.",
                    triggered_by="goal_reached_without_treatment_closure",
                ))