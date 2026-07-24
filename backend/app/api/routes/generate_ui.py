from fastapi import APIRouter

from app.domain.models.patient_record import PatientRecord
from app.domain.models.personalized_summary import PersonalizedSummary
from app.domain.models.pipeline_result import PipelineResult
from app.domain.ui_schema.dashboard_schema import DashboardSchema
from app.transformations.m2t_model_to_ui import transform_to_dashboard_schema
from pydantic import BaseModel

router = APIRouter()


class GenerateUIRequest(BaseModel):
    patient_record: PatientRecord
    personalized_summary: PersonalizedSummary


@router.post("/generate-ui", response_model=DashboardSchema)
async def generate_ui(payload: GenerateUIRequest) -> DashboardSchema:
    """Transformation M2T : convertit le PatientRecord + PersonalizedSummary
    en DashboardSchema, schéma déclaratif consommé par le frontend React."""
    pipeline_result = PipelineResult(
        patient_record=payload.patient_record,
        personalized_summary=payload.personalized_summary,
    )
    return transform_to_dashboard_schema(pipeline_result)