"""Test d'intégration du pipeline complet, avec un LLMClient mocké :
AUCUN appel réseau réel n'est effectué. Le mock retourne des réponses
JSON fixes (fixtures), ce qui rend le test rapide, gratuit et déterministe."""

import pytest

from app.agents.orchestrator_agent import OrchestratorAgent
from app.services.llm_client import LLMClient
from tests.fixtures.sample_notes import (
    DIABETES_NOTE,
    MOCK_EXTRACTION_JSON,
    MOCK_PERSONALIZATION_JSON,
)


class FakeLLMClient(LLMClient):
    """Faux client LLM pour les tests : retourne des réponses prédéfinies
    selon l'ordre d'appel (extraction en premier, personnalisation ensuite),
    sans jamais faire d'appel réseau réel."""

    def __init__(self) -> None:
        self._responses = [MOCK_EXTRACTION_JSON, MOCK_PERSONALIZATION_JSON]
        self._call_count = 0

    async def complete(self, system_prompt: str, user_message: str) -> str:
        response = self._responses[self._call_count]
        self._call_count += 1
        return response


@pytest.mark.asyncio
async def test_full_pipeline_produces_valid_result():
    orchestrator = OrchestratorAgent(llm_client=FakeLLMClient())
    result = await orchestrator.run(DIABETES_NOTE)

    assert result.patient_record.patient.first_name == "Marie"
    assert len(result.patient_record.diagnostics) == 1
    assert result.patient_record.diagnostics[0].label == "Diabète de type 2"
    assert result.personalized_summary.greeting == "Bonjour Marie,"


@pytest.mark.asyncio
async def test_full_pipeline_generates_no_alerts_for_clean_data():
    """Les données mockées sont volontairement 'propres' (confidence >= 0.9,
    posologie complète) : aucune alerte ne doit être générée."""
    orchestrator = OrchestratorAgent(llm_client=FakeLLMClient())
    result = await orchestrator.run(DIABETES_NOTE)

    assert len(result.patient_record.alerts) == 0
