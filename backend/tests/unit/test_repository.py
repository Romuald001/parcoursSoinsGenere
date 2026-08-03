"""Tests du repository : base SQLite en mémoire, aucun fichier créé,
aucun appel LLM. Rapide, isolé, reproductible."""

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base
from app.db.repository import get_goal_trend, get_or_create_patient, save_consultation
from app.domain.models.clinical_goal import ClinicalGoal
from app.domain.models.enums import Gender, HealthLiteracyLevel
from app.domain.models.patient import Patient
from app.domain.models.patient_record import PatientRecord
from app.domain.models.personalized_summary import PersonalizedSummary


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def make_record(current_value: float) -> PatientRecord:
    return PatientRecord(
        patient=Patient(
            first_name="Marie", last_name="Lambert",
            birth_date=date(1965, 3, 14),
            gender=Gender.FEMALE,
            health_literacy_level=HealthLiteracyLevel.LOW,
        ),
        clinical_goals=[ClinicalGoal(label="HbA1c", target_value=7.0, current_value=current_value, unit="%")],
    )


def make_summary() -> PersonalizedSummary:
    import uuid
    return PersonalizedSummary(patient_record_id=uuid.uuid4(), greeting="Bonjour", overview="Résumé")


def test_get_or_create_patient_deduplicates_by_identity(db_session):
    record = make_record(7.8)
    p1 = get_or_create_patient(db_session, record)
    p2 = get_or_create_patient(db_session, record)
    assert p1.id == p2.id


def test_goal_trend_reflects_multiple_consultations(db_session):
    record1 = make_record(7.8)
    patient = get_or_create_patient(db_session, record1)
    save_consultation(db_session, patient, "note 1", record1, make_summary())

    record2 = make_record(7.3)
    save_consultation(db_session, patient, "note 2", record2, make_summary())

    trend = get_goal_trend(db_session, patient.id, "HbA1c")
    assert len(trend) == 2
    assert trend[0]["current_value"] == 7.8
    assert trend[1]["current_value"] == 7.3


def test_get_user_by_identifier_matches_email_or_phone(db_session):
    from app.core.security import hash_password
    from app.db.models import UserORM
    from app.db.repository import get_user_by_identifier

    user = UserORM(email="a@example.com", phone="0600000000", hashed_password=hash_password("x"), role="patient")
    db_session.add(user)
    db_session.commit()

    assert get_user_by_identifier(db_session, "a@example.com").id == user.id
    assert get_user_by_identifier(db_session, "0600000000").id == user.id
    assert get_user_by_identifier(db_session, "inconnu") is None


def test_run_update_strips_alerts_from_previous_record():
    """Vérifie que l'Agent Extracteur ne transmet jamais les alertes
    du dossier précédent au LLM, et n'en renvoie jamais lui-même."""
    import asyncio
    from datetime import date
    from app.agents.extractor_agent import ExtractorAgent
    from app.domain.models.alert import Alert
    from app.domain.models.enums import AlertSeverity, Gender, HealthLiteracyLevel
    from app.domain.models.patient import Patient
    from app.domain.models.patient_record import PatientRecord
    from app.services.llm_client import LLMClient

    class SpyLLMClient(LLMClient):
        def __init__(self):
            self.last_user_message = None

        async def complete(self, system_prompt: str, user_message: str) -> str:
            self.last_user_message = user_message
            return '{"patient": {"first_name": "Marie", "last_name": "Dupont", "birth_date": "2000-01-01", "gender": "other", "health_literacy_level": "medium"}, "diagnostics": [], "medications": [], "treatment_steps": [], "clinical_goals": [], "appointments": []}'

    previous = PatientRecord(
        patient=Patient(
            first_name="Marie", last_name="Dupont", birth_date=date(2000, 1, 1),
            gender=Gender.OTHER, health_literacy_level=HealthLiteracyLevel.MEDIUM,
        ),
        alerts=[Alert(severity=AlertSeverity.WARNING, message="CECI_NE_DOIT_JAMAIS_ETRE_TRANSMIS", triggered_by="test")],
    )

    spy = SpyLLMClient()
    agent = ExtractorAgent(llm_client=spy)
    result = asyncio.run(agent.run_update(previous, "note de suivi"))

    assert result.alerts == []
    assert '"alerts":[]' in spy.last_user_message
    assert "CECI_NE_DOIT_JAMAIS_ETRE_TRANSMIS" not in spy.last_user_message