from app.agents.base import Agent
from app.domain.models.alert import Alert
from app.domain.models.enums import AlertSeverity
from app.domain.models.patient_record import PatientRecord


class VerifierAgent(Agent):
    """Agent Vérificateur : applique des règles métier déterministes
    (aucun appel LLM) sur un PatientRecord pour détecter incohérences
    et éléments à risque, et générer les Alert correspondantes."""

    LOW_CONFIDENCE_THRESHOLD = 0.6

    # Seuils cliniques standards (mmHg) pour la tension artérielle.
    SYSTOLIC_CRISIS_HIGH = 180.0
    SYSTOLIC_HYPOTENSION_LOW = 90.0
    DIASTOLIC_CRISIS_HIGH = 120.0
    DIASTOLIC_HYPOTENSION_LOW = 60.0

    async def run(self, record: PatientRecord) -> PatientRecord:
        self._check_low_confidence_items(record)
        self._check_vague_medications(record)
        self._check_achieved_goals_without_closure(record)
        self._check_abnormal_blood_pressure(record)
        return record

    def _check_low_confidence_items(self, record: PatientRecord) -> None:
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
        for medication in record.medications:
            if not medication.dosage.strip() or not medication.frequency.strip():
                record.add_alert(Alert(
                    severity=AlertSeverity.WARNING,
                    message=f"Le médicament '{medication.name}' a une posologie incomplète "
                            f"(dosage='{medication.dosage}', frequency='{medication.frequency}').",
                    triggered_by="incomplete_medication_dosage",
                ))

    def _check_achieved_goals_without_closure(self, record: PatientRecord) -> None:
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

    def _check_abnormal_blood_pressure(self, record: PatientRecord) -> None:
        """R5 : signale une valeur de tension artérielle cliniquement dangereuse
        (crise hypertensive ou hypotension sévère), selon des seuils médicaux
        standards. Correspondance par le label (insensible à la casse) plutôt
        que par un champ dédié, pour rester compatible avec le schéma
        générique ClinicalGoal existant."""
        for goal in record.clinical_goals:
            if goal.current_value is None:
                continue
            label_lower = goal.label.lower()

            if "systolique" in label_lower:
                if goal.current_value >= self.SYSTOLIC_CRISIS_HIGH:
                    record.add_alert(Alert(
                        severity=AlertSeverity.CRITICAL,
                        message=f"Tension systolique très élevée ({goal.current_value} mmHg) : "
                                f"risque de crise hypertensive, prise en charge urgente à envisager.",
                        triggered_by="hypertensive_crisis_systolic",
                    ))
                elif goal.current_value < self.SYSTOLIC_HYPOTENSION_LOW:
                    record.add_alert(Alert(
                        severity=AlertSeverity.CRITICAL,
                        message=f"Tension systolique très basse ({goal.current_value} mmHg) : "
                                f"risque d'hypotension sévère, à surveiller de près.",
                        triggered_by="hypotension_systolic",
                    ))

            elif "diastolique" in label_lower:
                if goal.current_value >= self.DIASTOLIC_CRISIS_HIGH:
                    record.add_alert(Alert(
                        severity=AlertSeverity.CRITICAL,
                        message=f"Tension diastolique très élevée ({goal.current_value} mmHg) : "
                                f"risque de crise hypertensive, prise en charge urgente à envisager.",
                        triggered_by="hypertensive_crisis_diastolic",
                    ))
                elif goal.current_value < self.DIASTOLIC_HYPOTENSION_LOW:
                    record.add_alert(Alert(
                        severity=AlertSeverity.CRITICAL,
                        message=f"Tension diastolique très basse ({goal.current_value} mmHg) : "
                                f"risque d'hypotension sévère, à surveiller de près.",
                        triggered_by="hypotension_diastolic",
                    ))
