from anthropic import AsyncAnthropic

from app.core.config import settings
from app.services.llm_client import LLMClient


class AnthropicClient(LLMClient):
    """Implémentation concrète de LLMClient utilisant l'API Anthropic (Claude)."""

    def __init__(self) -> None:
        if not settings.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY n'est pas configurée. "
                "Ajoute-la dans le fichier .env avant d'utiliser ce client."
            )
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def complete(self, system_prompt: str, user_message: str) -> str:
        response = await self._client.messages.create(
            model=settings.llm_model,
            max_tokens=settings.llm_max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        # La réponse peut contenir plusieurs blocs (texte, tool_use...).
        # On ne garde que les blocs texte, concaténés.
        text_blocks = [block.text for block in response.content if block.type == "text"]
        return "\n".join(text_blocks)