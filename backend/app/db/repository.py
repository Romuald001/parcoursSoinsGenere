import json

from sqlalchemy.orm import Session

from app.db.models import ConsultationORM, PatientORM, UserORM
from app.domain.models.patient_record import PatientRecord
from app.domain.models.personalized_summary import PersonalizedSummary


def get_or_create_patient(db: Session, record: PatientRecord) -> PatientORM:
    p = record.patient
    existing = (
        db.query(PatientORM)
        .filter_by(first_name=p.first_name, last_name=p.last_name, birth_date=p.birth_date.isoformat())
        .first()
    )
    if existing:
        return existing

    new_patient = PatientORM(
        first_name=p.first_name,
        last_name=p.last_name,
        birth_date=p.birth_date.isoformat(),
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient


def save_consultation(
    db: Session,
    patient: PatientORM,
    raw_note: str,
    record: PatientRecord,
    summary: PersonalizedSummary,
) -> ConsultationORM:
    consultation = ConsultationORM(
        patient_id=patient.id,
        raw_note=raw_note,
        patient_record_json=record.model_dump_json(),
        personalized_summary_json=summary.model_dump_json(),
    )
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation


def list_patients(db: Session) -> list[PatientORM]:
    return db.query(PatientORM).order_by(PatientORM.last_name).all()


def get_patient_consultations(db: Session, patient_id: str) -> list[ConsultationORM]:
    return (
        db.query(ConsultationORM)
        .filter_by(patient_id=patient_id)
        .order_by(ConsultationORM.created_at)
        .all()
    )


def get_goal_trend(db: Session, patient_id: str, goal_label: str) -> list[dict]:
    consultations = get_patient_consultations(db, patient_id)
    trend = []
    for c in consultations:
        data = json.loads(c.patient_record_json)
        for goal in data.get("clinical_goals", []):
            if goal["label"] == goal_label:
                trend.append({
                    "date": c.created_at.isoformat(),
                    "current_value": goal["current_value"],
                    "target_value": goal["target_value"],
                    "unit": goal["unit"],
                })
    return trend


def get_user_by_identifier(db: Session, identifier: str) -> UserORM | None:
    """Retrouve un utilisateur par email OU téléphone — un patient peut
    se connecter avec l'un ou l'autre selon ce qui a été renseigné."""
    return (
        db.query(UserORM)
        .filter((UserORM.email == identifier) | (UserORM.phone == identifier))
        .first()
    )
