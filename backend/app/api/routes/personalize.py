from fastapi import APIRouter, HTTPException

from app.agents.personalizer_agent import PersonalizationError, PersonalizerAgent
from app.domain.models.patient_record import PatientRecord
from app.domain.models.personalized_summary import PersonalizedSummary
from app.services.llm_factory import get_llm_client

router = APIRouter()


@router.post("/personalize", response_model=PersonalizedSummary)
async def personalize_summary(record: PatientRecord) -> PersonalizedSummary:
    """Génère un résumé vulgarisé du PatientRecord, adapté au niveau
    de littératie en santé du patient."""
    agent = PersonalizerAgent(llm_client=get_llm_client())
    try:
        return await agent.run(record)
    except PersonalizationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e