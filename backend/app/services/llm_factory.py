from app.core.config import settings
from app.services.llm_client import LLMClient


def get_llm_client() -> LLMClient:
    """Retourne l'implémentation LLMClient active selon la configuration (.env).

    Point d'entrée unique pour obtenir un client LLM : le reste du code
    (agents, endpoints) ne connaît jamais le provider concret utilisé.
    """
    if settings.llm_provider == "gemini":
        from app.services.gemini_client import GeminiClient
        return GeminiClient()

    if settings.llm_provider == "anthropic":
        from app.services.anthropic_client import AnthropicClient
        return AnthropicClient()

    raise ValueError(f"Fournisseur LLM inconnu : '{settings.llm_provider}'")