from fastapi import APIRouter, Depends

from app.agents.verifier_agent import VerifierAgent
from app.api.deps import require_doctor
from app.db.models import UserORM
from app.domain.models.patient_record import PatientRecord

router = APIRouter()


@router.post("/validate", response_model=PatientRecord)
async def validate_patient_record(
    record: PatientRecord, _doctor: UserORM = Depends(require_doctor)
) -> PatientRecord:
    """Applique les règles de vérification déterministes sur un PatientRecord
    et retourne le record enrichi des Alert détectées."""
    agent = VerifierAgent()
    return await agent.run(record)
