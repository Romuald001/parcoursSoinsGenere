from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.orchestrator_agent import OrchestratorAgent, PipelineError
from app.api.deps import require_doctor
from app.db.database import get_db
from app.db.models import UserORM
from app.db.repository import get_or_create_patient, save_consultation
from app.domain.ui_schema.dashboard_schema import DashboardSchema
from app.services.llm_factory import get_llm_client
from app.transformations.m2t_model_to_ui import transform_to_dashboard_schema

router = APIRouter()


class PipelineRequest(BaseModel):
    raw_note: str


@router.post("/pipeline/run", response_model=DashboardSchema)
async def run_full_pipeline(
    payload: PipelineRequest,
    response: Response,
    db: Session = Depends(get_db),
    doctor: UserORM = Depends(require_doctor),
) -> DashboardSchema:
    orchestrator = OrchestratorAgent(llm_client=get_llm_client())
    try:
        result = await orchestrator.run(payload.raw_note)
    except PipelineError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    patient_orm = get_or_create_patient(db, result.patient_record)
    save_consultation(db, patient_orm, payload.raw_note, result.patient_record, result.personalized_summary, doctor)
    response.headers["X-Patient-Id"] = patient_orm.id
    response.headers["X-Doctor-Name"] = doctor.full_name or doctor.email or "Médecin"

    return transform_to_dashboard_schema(result)
