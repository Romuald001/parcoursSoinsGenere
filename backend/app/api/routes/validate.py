from fastapi import APIRouter

from app.agents.verifier_agent import VerifierAgent
from app.domain.models.patient_record import PatientRecord

router = APIRouter()


@router.post("/validate", response_model=PatientRecord)
async def validate_patient_record(record: PatientRecord) -> PatientRecord:
    """Applique les règles de vérification déterministes sur un PatientRecord
    et retourne le record enrichi des Alert détectées."""
    agent = VerifierAgent()
    return await agent.run(record)