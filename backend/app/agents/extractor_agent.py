import json
import re

from app.domain.models.patient_record import PatientRecord
from app.prompts.extractor_prompt import EXTRACTOR_SYSTEM_PROMPT
from app.services.llm_client import LLMClient
from app.agents.base import Agent


class ExtractionError(Exception):
    """Levée quand la réponse du LLM ne peut pas être transformée en PatientRecord valide."""


class ExtractorAgent(Agent):
    """Agent Extracteur : transforme une note médicale en texte libre
    en un PatientRecord structuré et validé (transformation M2M)."""

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm_client = llm_client

    async def run(self, raw_note: str) -> PatientRecord:
        raw_response = await self._llm_client.complete(
            system_prompt=EXTRACTOR_SYSTEM_PROMPT,
            user_message=raw_note,
        )
        json_text = self._extract_json_block(raw_response)

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ExtractionError(
                f"La réponse du LLM n'est pas un JSON valide : {e}\nRéponse brute : {raw_response}"
            ) from e

        try:
            return PatientRecord.model_validate(data)
        except Exception as e:
            raise ExtractionError(
                f"Le JSON extrait ne respecte pas le schéma PatientRecord : {e}"
            ) from e

    @staticmethod
    def _extract_json_block(text: str) -> str:
        """Nettoie la réponse du LLM au cas où il aurait entouré le JSON de balises markdown
        malgré la consigne (défense en profondeur, comportement LLM non 100% déterministe)."""
        match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
        if match:
            return match.group(1)
        return text.strip()