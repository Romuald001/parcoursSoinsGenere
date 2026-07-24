import asyncio
from app.agents.verifier_agent import VerifierAgent
from app.domain.models.patient_record import PatientRecord
from app.domain.models.patient import Patient
from app.domain.models.medication import Medication
from app.domain.models.clinical_goal import ClinicalGoal
from app.domain.models.enums import Gender, HealthLiteracyLevel
from datetime import date

record = PatientRecord(
    patient=Patient(
        first_name="Test", last_name="Patient",
        birth_date=date(1990, 1, 1),
        gender=Gender.OTHER,
        health_literacy_level=HealthLiteracyLevel.MEDIUM,
    ),
    medications=[
        Medication(name="Aspirine", dosage="", frequency="1x/jour", confidence=0.9),
    ],
    clinical_goals=[
        ClinicalGoal(label="Tension", target_value=13.0, current_value=12.0, unit="mmHg"),
    ],
)

async def main():
    verifier = VerifierAgent()
    result = await verifier.run(record)
    for alert in result.alerts:
        print(f"- [{alert.severity.value}] {alert.message}")

asyncio.run(main())
