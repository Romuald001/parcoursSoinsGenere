from typing import Literal, Union

from pydantic import BaseModel, Field


class PatientHeaderData(BaseModel):
    """Bandeau d'en-tête du dashboard : identité et message d'accueil."""
    full_name: str
    age: int
    greeting: str


class CardWidget(BaseModel):
    """Widget générique de type 'carte' : utilisé pour diagnostics et médicaments."""
    type: Literal["card"] = "card"
    id: str
    title: str
    subtitle: str | None = None
    description: str | None = None
    confidence_badge: float | None = Field(
        default=None,
        description="Affiché uniquement si < 1.0, pour signaler une info à faible certitude."
    )


class AlertWidgetItem(BaseModel):
    """Une alerte individuelle affichée dans l'AlertWidget."""
    severity: Literal["info", "warning", "critical"]
    message: str


class AlertWidget(BaseModel):
    """Widget regroupant toutes les alertes actives du patient."""
    type: Literal["alert"] = "alert"
    id: str
    items: list[AlertWidgetItem] = Field(default_factory=list)


class TimelineEvent(BaseModel):
    """Un événement individuel de la frise chronologique."""
    label: str
    date: str | None = None
    status: str | None = None


class TimelineWidget(BaseModel):
    """Widget de frise chronologique : étapes de traitement + rendez-vous, triés par date."""
    type: Literal["timeline"] = "timeline"
    id: str
    events: list[TimelineEvent] = Field(default_factory=list)


class GoalProgressWidget(BaseModel):
    """Widget de barre de progression pour un objectif clinique."""
    type: Literal["goal_progress"] = "goal_progress"
    id: str
    label: str
    current_value: float
    target_value: float
    unit: str
    progress_percent: float = Field(
        description="Pourcentage de progression vers l'objectif, calculé côté backend "
                    "(0-100), pour éviter toute logique de calcul métier côté frontend."
    )


# Union discriminée : le champ "type" permet au frontend de savoir
# quel composant React instancier pour chaque widget (voir widgetRegistry.ts)
Widget = Union[CardWidget, AlertWidget, TimelineWidget, GoalProgressWidget]


class DashboardSection(BaseModel):
    """Une section du dashboard, regroupant plusieurs widgets sous un titre commun."""
    title: str
    widgets: list[Widget] = Field(default_factory=list)


class DashboardSchema(BaseModel):
    """Schéma complet du dashboard patient : objet final transmis au frontend,
    consommé par le moteur de rendu générique (DashboardRenderer.tsx)."""
    patient_header: PatientHeaderData
    sections: list[DashboardSection] = Field(default_factory=list)