"""Tests unitaires du métamodèle : vérifie que les contraintes OCL
définies à l'Étape 1 sont bien appliquées par Pydantic (Étape 2)."""

import pytest
from datetime import date

from app.domain.models.alert import Alert
from app.domain.models.clinical_goal import ClinicalGoal
from app.domain.models.enums import AlertSeverity, Gender, HealthLiteracyLevel
from app.domain.models.medication import Medication
from app.domain.models.patient import Patient
from app.domain.models.treatment_step import TreatmentStep
from app.domain.models.enums import TreatmentStatus


def test_patient_age_is_computed_correctly():
    patient = Patient(
        first_name="Jean", last_name="Dupont",
        birth_date=date(1980, 5, 12),
        gender=Gender.MALE,
        health_literacy_level=HealthLiteracyLevel.MEDIUM,
    )
    assert patient.age == date.today().year - 1980 - (
        (date.today().month, date.today().day) < (5, 12)
    )


def test_critical_alert_without_cause_is_rejected():
    with pytest.raises(ValueError, match="triggered_by"):
        Alert(severity=AlertSeverity.CRITICAL, message="Risque détecté")


def test_critical_alert_with_cause_is_accepted():
    alert = Alert(
        severity=AlertSeverity.CRITICAL,
        message="Risque détecté",
        triggered_by="interaction_medicamenteuse",
    )
    assert alert.triggered_by == "interaction_medicamenteuse"


def test_medication_end_date_before_start_date_is_rejected():
    with pytest.raises(ValueError, match="antérieure"):
        Medication(
            name="Aspirine", dosage="500mg", frequency="1x/jour",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 5, 1),
        )


def test_clinical_goal_without_unit_but_with_value_is_rejected():
    with pytest.raises(ValueError, match="unité"):
        ClinicalGoal(label="Tension", target_value=13.0)


def test_clinical_goal_with_unit_is_accepted():
    goal = ClinicalGoal(label="Tension", target_value=13.0, current_value=12.0, unit="mmHg")
    assert goal.unit == "mmHg"


def test_treatment_step_done_without_scheduled_date_is_rejected():
    with pytest.raises(ValueError, match="scheduled_date"):
        TreatmentStep(label="Consultation", status=TreatmentStatus.DONE)


def test_treatment_step_done_with_future_date_is_rejected():
    with pytest.raises(ValueError, match="future"):
        TreatmentStep(
            label="Consultation",
            status=TreatmentStatus.DONE,
            scheduled_date=date(2099, 1, 1),
        )
