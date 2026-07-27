import json

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.orchestrator_agent import OrchestratorAgent, PipelineError
from app.api.deps import get_current_user, require_doctor
from app.db.database import get_db
from app.db.models import UserORM
from app.db.repository import (
    get_consultation_by_id,
    get_doctor_display_name,
    get_goal_trend,
    get_patient_by_id,
    get_patient_consultations,
    list_patients,
    save_consultation,
)
from app.domain.models.patient_record import PatientRecord
from app.domain.models.personalized_summary import PersonalizedSummary
from app.domain.models.pipeline_result import PipelineResult
from app.domain.ui_schema.dashboard_schema import DashboardSchema
from app.services.llm_factory import get_llm_client
from app.transformations.m2t_model_to_ui import transform_to_dashboard_schema

router = APIRouter()


def _check_access(user: UserORM, patient_id: str) -> None:
    if user.role == "patient" and user.patient_id != patient_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à ce dossier.")


@router.get("/patients")
def get_patients(db: Session = Depends(get_db), _doctor: UserORM = Depends(require_doctor)):
    """Tous les médecins voient tous les patients (continuité de soins :
    un médecin absent ou indisponible ne bloque pas l'accès au dossier)."""
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
    _check_access(user, patient_id)

    consultations = get_patient_consultations(db, patient_id)
    if not consultations:
        raise HTTPException(status_code=404, detail="Aucune consultation trouvée pour ce patient.")

    result = []
    for c in consultations:
        record_data = json.loads(c.patient_record_json)
        result.append({
            "id": c.id,
            "created_at": c.created_at.isoformat(),
            "raw_note": c.raw_note,
            "doctor_name": get_doctor_display_name(db, c.doctor_id),
            "diagnostics": [d["label"] for d in record_data.get("diagnostics", [])],
            "clinical_goals": [
                {"label": g["label"], "unit": g.get("unit")}
                for g in record_data.get("clinical_goals", [])
                if g.get("unit")
            ],
        })
    return result


@router.get("/patients/{patient_id}/consultations/{consultation_id}/dashboard")
def get_consultation_dashboard(
    patient_id: str,
    consultation_id: str,
    response: Response,
    db: Session = Depends(get_db),
    user: UserORM = Depends(get_current_user),
):
    """Régénère le DashboardSchema tel qu'il était lors d'une consultation
    précise (pas forcément la plus récente) — permet de revoir l'historique."""
    _check_access(user, patient_id)

    consultation = get_consultation_by_id(db, consultation_id)
    if not consultation or consultation.patient_id != patient_id:
        raise HTTPException(status_code=404, detail="Consultation introuvable.")

    record = PatientRecord.model_validate_json(consultation.patient_record_json)
    summary = PersonalizedSummary.model_validate_json(consultation.personalized_summary_json)
    response.headers["X-Doctor-Name"] = get_doctor_display_name(db, consultation.doctor_id) or "Médecin"
    return transform_to_dashboard_schema(PipelineResult(patient_record=record, personalized_summary=summary))


class ContinueConsultationRequest(BaseModel):
    raw_note: str


@router.post("/patients/{patient_id}/continue", response_model=DashboardSchema)
async def continue_consultation(
    patient_id: str,
    payload: ContinueConsultationRequest,
    response: Response,
    db: Session = Depends(get_db),
    doctor: UserORM = Depends(require_doctor),
) -> DashboardSchema:
    """Ajoute une note de suivi au dossier existant d'un patient : le
    dossier précédent sert de contexte, la nouvelle note vient le compléter
    ou le mettre à jour (continuité de soins, pas une ré-extraction à zéro)."""
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient introuvable.")

    consultations = get_patient_consultations(db, patient_id)
    if not consultations:
        raise HTTPException(status_code=404, detail="Aucune consultation existante pour ce patient.")

    previous_record = PatientRecord.model_validate_json(consultations[-1].patient_record_json)

    orchestrator = OrchestratorAgent(llm_client=get_llm_client())
    try:
        result = await orchestrator.run_continuation(previous_record, payload.raw_note)
    except PipelineError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    save_consultation(db, patient, payload.raw_note, result.patient_record, result.personalized_summary, doctor)
    response.headers["X-Doctor-Name"] = doctor.full_name or doctor.email or "Médecin"

    return transform_to_dashboard_schema(result)


@router.get("/patients/{patient_id}/goal-trend/{goal_label}")
def get_trend(
    patient_id: str, goal_label: str, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)
):
    _check_access(user, patient_id)

    trend = get_goal_trend(db, patient_id, goal_label)
    if not trend:
        raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour cet objectif.")
    return trend


@router.get("/me/dashboard")
def get_my_dashboard(response: Response, db: Session = Depends(get_db), user: UserORM = Depends(get_current_user)):
    if user.role != "patient" or not user.patient_id:
        raise HTTPException(status_code=403, detail="Réservé aux comptes patient.")

    consultations = get_patient_consultations(db, user.patient_id)
    if not consultations:
        raise HTTPException(status_code=404, detail="Aucune consultation trouvée.")

    latest = consultations[-1]
    record = PatientRecord.model_validate_json(latest.patient_record_json)
    summary = PersonalizedSummary.model_validate_json(latest.personalized_summary_json)
    response.headers["X-Doctor-Name"] = get_doctor_display_name(db, latest.doctor_id) or "Médecin"
    return transform_to_dashboard_schema(PipelineResult(patient_record=record, personalized_summary=summary))
