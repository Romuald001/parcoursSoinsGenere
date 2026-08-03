import json
import re

from app.domain.models.patient_record import PatientRecord
from app.prompts.extractor_prompt import EXTRACTOR_SYSTEM_PROMPT
from app.prompts.extractor_update_prompt import EXTRACTOR_UPDATE_SYSTEM_PROMPT
from app.services.llm_client import LLMClient
from app.agents.base import Agent


class ExtractionError(Exception):
    """Levée quand la réponse du LLM ne peut pas être transformée en PatientRecord valide."""


class ExtractorAgent(Agent):
    """Agent Extracteur : transforme une note médicale en texte libre
    en un PatientRecord structuré et validé (transformation M2M).

    Supporte aussi la MISE À JOUR d'un dossier existant à partir d'une
    nouvelle note (continuité de soins), via run_update()."""

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm_client = llm_client

    async def run(self, raw_note: str) -> PatientRecord:
        raw_response = await self._llm_client.complete(
            system_prompt=EXTRACTOR_SYSTEM_PROMPT,
            user_message=raw_note,
        )
        return self._parse_response(raw_response)

    async def run_update(self, previous_record: PatientRecord, raw_note: str) -> PatientRecord:
        """Met à jour un dossier existant à partir d'une nouvelle note,
        en conservant l'historique clinique pertinent (pas une ré-extraction
        depuis zéro).

        Important : les 'alerts' du dossier précédent ne sont JAMAIS transmises
        au LLM. Les alertes sont produites exclusivement par l'Agent Vérificateur
        (règles déterministes), pas par l'Agent Extracteur — les lui transmettre
        créait une confusion qui faisait halluciner des objets Alert incomplets."""
        clean_previous = previous_record.model_copy(update={"alerts": []})

        user_message = (
            f"DOSSIER ACTUEL:\n{clean_previous.model_dump_json()}\n\n"
            f"NOUVELLE NOTE:\n{raw_note}"
        )
        raw_response = await self._llm_client.complete(
            system_prompt=EXTRACTOR_UPDATE_SYSTEM_PROMPT,
            user_message=user_message,
        )
        record = self._parse_response(raw_response)

        # Sécurité supplémentaire : même si le LLM ignorait la consigne et
        # renvoyait quand même un champ "alerts", on ne lui fait jamais confiance
        # pour ce champ — on le réinitialise systématiquement côté code.
        return record.model_copy(update={"alerts": []})

    def _parse_response(self, raw_response: str) -> PatientRecord:
        json_text = self._extract_json_block(raw_response)
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ExtractionError(
                f"La réponse du LLM n'est pas un JSON valide : {e}\nRéponse brute : {raw_response}"
            ) from e
        data.pop("alerts", None)  # défense en profondeur avant même la validation Pydantic
        try:
            return PatientRecord.model_validate(data)
        except Exception as e:
            raise ExtractionError(
                f"Le JSON extrait ne respecte pas le schéma PatientRecord : {e}"
            ) from e

    @staticmethod
    def _extract_json_block(text: str) -> str:
        match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
        if match:
            return match.group(1)
        return text.strip()
