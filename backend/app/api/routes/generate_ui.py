from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_doctor
from app.db.database import get_db
from app.db.models import UserORM
from app.db.repository import get_or_create_patient, save_consultation
from app.domain.models.patient_record import PatientRecord
from app.domain.models.personalized_summary import PersonalizedSummary
from app.domain.models.pipeline_result import PipelineResult
from app.domain.ui_schema.dashboard_schema import DashboardSchema
from app.transformations.m2t_model_to_ui import transform_to_dashboard_schema

router = APIRouter()


class GenerateUIRequest(BaseModel):
    patient_record: PatientRecord
    personalized_summary: PersonalizedSummary


@router.post("/generate-ui", response_model=DashboardSchema)
async def generate_ui(
    payload: GenerateUIRequest,
    response: Response,
    db: Session = Depends(get_db),
    _doctor: UserORM = Depends(require_doctor),
) -> DashboardSchema:
    pipeline_result = PipelineResult(
        patient_record=payload.patient_record,
        personalized_summary=payload.personalized_summary,
    )

    patient_orm = get_or_create_patient(db, payload.patient_record)
    save_consultation(db, patient_orm, "", payload.patient_record, payload.personalized_summary)
    response.headers["X-Patient-Id"] = patient_orm.id

    return transform_to_dashboard_schema(pipeline_result)
