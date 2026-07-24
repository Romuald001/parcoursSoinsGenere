from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class PersonalizedSummary(BaseModel):
    """Résumé du parcours de soins, rédigé dans un langage adapté
    au niveau de littératie en santé du patient (health_literacy_level).

    Cet objet est un contenu DÉRIVÉ, distinct du PatientRecord :
    il ne modifie jamais les données médicales structurées,
    il en propose uniquement une présentation vulgarisée pour l'utilisateur final."""

    id: UUID = Field(default_factory=uuid4)
    patient_record_id: UUID = Field(
        description="Référence vers le PatientRecord dont ce résumé est dérivé."
    )
    greeting: str = Field(
        description="Phrase d'accueil personnalisée pour le patient."
    )
    overview: str = Field(
        description="Résumé global de la situation, en langage simple."
    )
    key_priorities: list[str] = Field(
        default_factory=list,
        description="Liste courte des points les plus importants à retenir, "
                    "ordonnés par priorité."
    )
    simplified_glossary: dict[str, str] = Field(
        default_factory=dict,
        description="Termes médicaux techniques du dossier, associés à leur "
                    "explication simple (ex: 'HbA1c' -> 'un indicateur du taux de sucre dans le sang')."
    )