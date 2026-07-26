from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.agents.extractor_agent import ExtractionError, ExtractorAgent
from app.api.deps import require_doctor
from app.db.models import UserORM
from app.domain.models.patient_record import PatientRecord
from app.services.llm_factory import get_llm_client

router = APIRouter()


class ExtractRequest(BaseModel):
    raw_note: str


@router.post("/extract", response_model=PatientRecord)
async def extract_patient_record(
    payload: ExtractRequest, _doctor: UserORM = Depends(require_doctor)
) -> PatientRecord:
    """Transforme une note médicale en texte libre en un PatientRecord structuré."""
    agent = ExtractorAgent(llm_client=get_llm_client())
    try:
        return await agent.run(payload.raw_note)
    except ExtractionError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
