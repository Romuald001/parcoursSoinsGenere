from datetime import date
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.models.enums import Gender, HealthLiteracyLevel


class Patient(BaseModel):
    """Racine d'agrégation du métamodèle : représente le patient
    et regroupe (par référence) l'ensemble de son parcours de soins."""

    id: UUID = Field(default_factory=uuid4)
    first_name: str
    last_name: str
    birth_date: date
    gender: Gender
    health_literacy_level: HealthLiteracyLevel = Field(
        default=HealthLiteracyLevel.MEDIUM,
        description="Détermine le niveau de simplification du langage "
                    "appliqué par l'Agent Personnalisateur.",
    )

    @property
    def age(self) -> int:
        """Calcule l'âge à partir de la date de naissance.
        Utile pour l'Agent Personnalisateur (ex: adapter le ton pour un enfant)."""
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )