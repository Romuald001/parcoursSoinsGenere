from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    """Interface abstraite commune à tous les agents du système multi-agents (SMA)."""

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> Any:
        """Exécute la tâche métier de l'agent."""
        raise NotImplementedError