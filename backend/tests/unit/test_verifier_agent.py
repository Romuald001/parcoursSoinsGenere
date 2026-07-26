"""Tests unitaires de l'Agent Vérificateur : règles 100% déterministes,
AUCUN appel LLM nécessaire pour ces tests (argument clé de testabilité)."""

import pytest
from datetime import date

from app.agents.verifier_agent import VerifierAgent
from app.domain.models.clinical_goal import ClinicalGoal
from app.domain.models.diagnostic import Diagnostic
from app.domain.models.enums import Gender, HealthLiteracyLevel
from app.domain.models.medication import Medication
from app.domain.models.patient import Patient
from app.domain.models.patient_record import PatientRecord


def make_base_record(**overrides) -> PatientRecord:
    """Fabrique un PatientRecord minimal pour les tests, personnalisable."""
    defaults = dict(
        patient=Patient(
            first_name="Test", last_name="Patient",
            birth_date=date(1990, 1, 1),
            gender=Gender.OTHER,
            health_literacy_level=HealthLiteracyLevel.MEDIUM,
        ),
    )
    defaults.update(overrides)
    return PatientRecord(**defaults)


@pytest.mark.asyncio
async def test_low_confidence_diagnostic_triggers_alert():
    record = make_base_record(
        diagnostics=[Diagnostic(label="Diagnostic incertain", confidence=0.3)]
    )
    result = await VerifierAgent().run(record)
    assert len(result.alerts) == 1
    assert result.alerts[0].triggered_by == "low_confidence_diagnostic"


@pytest.mark.asyncio
async def test_high_confidence_diagnostic_triggers_no_alert():
    record = make_base_record(
        diagnostics=[Diagnostic(label="Diagnostic certain", confidence=0.95)]
    )
    result = await VerifierAgent().run(record)
    assert len(result.alerts) == 0


@pytest.mark.asyncio
async def test_medication_with_empty_dosage_triggers_alert():
    record = make_base_record(
        medications=[Medication(name="Aspirine", dosage="", frequency="1x/jour", confidence=0.9)]
    )
    result = await VerifierAgent().run(record)
    assert any(a.triggered_by == "incomplete_medication_dosage" for a in result.alerts)


@pytest.mark.asyncio
async def test_goal_reached_without_treatment_closure_triggers_info_alert():
    record = make_base_record(
        clinical_goals=[
            ClinicalGoal(label="Tension", target_value=13.0, current_value=12.0, unit="mmHg")
        ]
    )
    result = await VerifierAgent().run(record)
    assert any(a.triggered_by == "goal_reached_without_treatment_closure" for a in result.alerts)


@pytest.mark.asyncio
async def test_goal_not_reached_triggers_no_alert():
    record = make_base_record(
        clinical_goals=[
            ClinicalGoal(label="Tension", target_value=13.0, current_value=15.0, unit="mmHg")
        ]
    )
    result = await VerifierAgent().run(record)
    assert len(result.alerts) == 0
