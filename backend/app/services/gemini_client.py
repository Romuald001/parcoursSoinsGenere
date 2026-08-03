import asyncio

from google import genai
from google.genai import errors, types

from app.core.config import settings
from app.services.llm_client import LLMClient


class GeminiClient(LLMClient):
    """Implémentation de LLMClient utilisant l'API Gemini (Google AI Studio, tier gratuit).

    Inclut une nouvelle tentative automatique en cas d'erreur serveur
    temporaire (503 UNAVAILABLE, surcharge du fournisseur) : ce type
    d'erreur n'est pas lié à notre code, mais il serait dommage de faire
    échouer toute une consultation pour un incident transitoire de
    quelques secondes côté Google."""

    MAX_RETRIES = 2
    RETRY_DELAY_SECONDS = 3

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY n'est pas configurée. "
                "Ajoute-la dans le fichier .env (récupérable sur https://aistudio.google.com/apikey)."
            )
        self._client = genai.Client(api_key=settings.gemini_api_key)

    async def complete(self, system_prompt: str, user_message: str) -> str:
        last_error: Exception | None = None

        for attempt in range(1 + self.MAX_RETRIES):
            try:
                response = await self._client.aio.models.generate_content(
                    model=settings.gemini_model,
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                    ),
                )
                return response.text
            except errors.ServerError as e:
                last_error = e
                if attempt < self.MAX_RETRIES:
                    await asyncio.sleep(self.RETRY_DELAY_SECONDS)
                    continue

        raise RuntimeError(
            "Le service Gemini est temporairement surchargé (erreur serveur 503). "
            "Ceci est un incident côté fournisseur, indépendant de votre note ou du "
            "traitement effectué. Merci de réessayer dans quelques instants."
        ) from last_error
