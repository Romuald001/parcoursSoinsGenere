from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Interface abstraite pour tout client LLM.

    Toute nouvelle implémentation (Anthropic, OpenAI, Ollama local, etc.)
    doit respecter ce contrat. Les agents ne dépendent JAMAIS d'une
    implémentation concrète, uniquement de cette abstraction
    (principe d'inversion de dépendance - Clean Architecture)."""

    @abstractmethod
    async def complete(self, system_prompt: str, user_message: str) -> str:
        """Envoie un prompt système + message utilisateur, retourne le texte brut de la réponse.

        Args:
            system_prompt: instructions de rôle/comportement pour le modèle
            user_message: contenu à traiter (ex: la note du médecin)

        Returns:
            La réponse textuelle brute du modèle (à parser ensuite par l'appelant)
        """
        raise NotImplementedError