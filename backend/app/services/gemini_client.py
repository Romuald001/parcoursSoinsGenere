from google import genai
from google.genai import types

from app.core.config import settings
from app.services.llm_client import LLMClient


class GeminiClient(LLMClient):
    """Implémentation de LLMClient utilisant l'API Gemini (Google AI Studio, tier gratuit)."""

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY n'est pas configurée. "
                "Ajoute-la dans le fichier .env (récupérable sur https://aistudio.google.com/apikey)."
            )
        self._client = genai.Client(api_key=settings.gemini_api_key)

    async def complete(self, system_prompt: str, user_message: str) -> str:
        response = await self._client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            ),
        )
        return response.text