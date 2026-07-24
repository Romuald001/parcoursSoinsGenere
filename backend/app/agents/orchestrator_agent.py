from app.agents.base import Agent
from app.agents.extractor_agent import ExtractorAgent, ExtractionError
from app.agents.personalizer_agent import PersonalizerAgent, PersonalizationError
from app.agents.verifier_agent import VerifierAgent
from app.domain.models.pipeline_result import PipelineResult
from app.services.llm_client import LLMClient


class PipelineError(Exception):
    """Erreur levée par l'Orchestrateur en cas d'échec à n'importe quelle
    étape du pipeline (extraction, vérification, personnalisation)."""


class OrchestratorAgent(Agent):
    """Agent Orchestrateur : coordonne le pipeline complet
    Extraction -> Vérification -> Personnalisation.

    Ne contient aucune logique métier propre : délègue entièrement
    aux agents spécialisés (pattern Mediator)."""

    def __init__(self, llm_client: LLMClient) -> None:
        self._extractor = ExtractorAgent(llm_client=llm_client)
        self._verifier = VerifierAgent()
        self._personalizer = PersonalizerAgent(llm_client=llm_client)

    async def run(self, raw_note: str) -> PipelineResult:
        try:
            record = await self._extractor.run(raw_note)
        except ExtractionError as e:
            raise PipelineError(f"Échec à l'étape d'extraction : {e}") from e

        record = await self._verifier.run(record)

        try:
            summary = await self._personalizer.run(record)
        except PersonalizationError as e:
            raise PipelineError(f"Échec à l'étape de personnalisation : {e}") from e

        return PipelineResult(
            patient_record=record,
            personalized_summary=summary,
        )