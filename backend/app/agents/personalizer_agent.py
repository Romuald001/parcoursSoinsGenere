import json
import re

from app.agents.base import Agent
from app.domain.models.patient_record import PatientRecord
from app.domain.models.personalized_summary import PersonalizedSummary
from app.prompts.personalizer_prompt import PERSONALIZER_SYSTEM_PROMPT_TEMPLATE
from app.services.llm_client import LLMClient


class PersonalizationError(Exception):
    """Levée quand la réponse du LLM ne peut pas être transformée en PersonalizedSummary valide."""


class PersonalizerAgent(Agent):
    """Agent Personnalisateur : génère un résumé vulgarisé du PatientRecord,
    adapté au niveau de littératie en santé du patient (transformation M2M)."""

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm_client = llm_client

    async def run(self, record: PatientRecord) -> PersonalizedSummary:
        system_prompt = PERSONALIZER_SYSTEM_PROMPT_TEMPLATE.format(
            literacy_level=record.patient.health_literacy_level.value
        )
        record_json = record.model_dump_json()

        raw_response = await self._llm_client.complete(
            system_prompt=system_prompt,
            user_message=record_json,
        )
        json_text = self._extract_json_block(raw_response)

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            raise PersonalizationError(
                f"La réponse du LLM n'est pas un JSON valide : {e}\nRéponse brute : {raw_response}"
            ) from e

        data["patient_record_id"] = str(record.id)

        try:
            return PersonalizedSummary.model_validate(data)
        except Exception as e:
            raise PersonalizationError(
                f"Le JSON extrait ne respecte pas le schéma PersonalizedSummary : {e}"
            ) from e

    @staticmethod
    def _extract_json_block(text: str) -> str:
        """Même logique défensive que l'ExtractorAgent : nettoyage des balises markdown."""
        match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
        if match:
            return match.group(1)
        return text.strip()