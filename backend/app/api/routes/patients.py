from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_doctor
from app.db.database import get_db
from app.db.models import UserORM
from app.db.repository import get_goal_trend, get_patient_consultations, list_patients
from app.domain.models.patient_record import PatientRecord
from app.domain.models.personalized_summary import PersonalizedSummary
from app.domain.models.pipeline_result import PipelineResult
from app.transformations.m2t_model_to_ui import transform_to_dashboard_schema

router = APIRouter()


@router.get("/patients")
def get_patients(db: Session = Depends(get_db), _doctor: UserORM = Depends(require_doctor)):
    """Réservé aux médecins : liste de tous les patients suivis."""
    patients = list_patients(db)
    return [
        {
            "id": p.id,
            "full_name": f"{p.first_name} {p.last_name}",
            "birth_date": p.birth_date,
            "consultation_count": len(p.consultations),
        }
        for p in patients
    ]


@router.get("/patients/{patient_id}/consultations")
def get_consultations(patient_id: str, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    """Accessible par un médecin (tout dossier) ou par le patient concerné
    (uniquement son propre dossier)."""
    if user.role == "patient" and user.patient_id != patient_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à ce dossier.")

    consultations = get_patient_consultations(db, patient_id)
    if not consultations:
        raise HTTPException(status_code=404, detail="Aucune consultation trouvée pour ce patient.")
    return [
        {"id": c.id, "created_at": c.created_at.isoformat(), "raw_note": c.raw_note}
        for c in consultations
    ]


@router.get("/patients/{patient_id}/goal-trend/{goal_label}")
def get_trend(
    patient_id: str, goal_label: str, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)
):
    if user.role == "patient" and user.patient_id != patient_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à ce dossier.")

    trend = get_goal_trend(db, patient_id, goal_label)
    if not trend:
        raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour cet objectif.")
    return trend


@router.get("/me/dashboard")
def get_my_dashboard(db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    """Réservé aux comptes patient : renvoie le dashboard de la consultation
    la plus récente de l'utilisateur connecté."""
    if user.role != "patient" or not user.patient_id:
        raise HTTPException(status_code=403, detail="Réservé aux comptes patient.")

    consultations = get_patient_consultations(db, user.patient_id)
    if not consultations:
        raise HTTPException(status_code=404, detail="Aucune consultation trouvée.")

    latest = consultations[-1]
    record = PatientRecord.model_validate_json(latest.patient_record_json)
    summary = PersonalizedSummary.model_validate_json(latest.personalized_summary_json)
    return transform_to_dashboard_schema(PipelineResult(patient_record=record, personalized_summary=summary))
