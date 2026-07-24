from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration centralisée de l'application, lue depuis les variables d'environnement."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Parcours de Soins Généré"
    environment: str = "development"

    # Fournisseur LLM actif : "anthropic" | "gemini" | "ollama"
    llm_provider: str = "gemini"

    # Anthropic (optionnel, si crédits disponibles plus tard)
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"
    llm_max_tokens: int = 4096

    # Gemini (tier gratuit)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"


settings = Settings()