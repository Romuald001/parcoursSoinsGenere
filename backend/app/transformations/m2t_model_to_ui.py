from app.domain.models.pipeline_result import PipelineResult
from app.domain.models.enums import TreatmentStatus
from app.domain.ui_schema.dashboard_schema import (
    AlertWidget,
    AlertWidgetItem,
    CardWidget,
    DashboardSchema,
    DashboardSection,
    GoalProgressWidget,
    PatientHeaderData,
    TimelineEvent,
    TimelineWidget,
)


def transform_to_dashboard_schema(pipeline_result: PipelineResult) -> DashboardSchema:
    """Transformation M2T : convertit le PipelineResult (modèle métier validé)
    en DashboardSchema (schéma déclaratif consommé par le frontend React).

    Aucune logique médicale ici : uniquement du mapping et des calculs
    de présentation (pourcentages, tri chronologique)."""

    record = pipeline_result.patient_record
    summary = pipeline_result.personalized_summary

    header = PatientHeaderData(
        full_name=f"{record.patient.first_name} {record.patient.last_name}",
        age=record.patient.age,
        greeting=summary.greeting,
    )

    sections: list[DashboardSection] = []

    # Section "Résumé" : overview + priorités, sous forme de cartes
    overview_cards: list = [
        CardWidget(id="overview", title="Votre situation", description=summary.overview)
    ]
    for i, priority in enumerate(summary.key_priorities):
        overview_cards.append(
            CardWidget(id=f"priority-{i}", title="À retenir", description=priority)
        )
    sections.append(DashboardSection(title="Résumé", widgets=overview_cards))

    # Section "Alertes" : uniquement si des alertes existent (pas de section vide)
    if record.alerts:
        alert_items = [
            AlertWidgetItem(severity=a.severity.value, message=a.message)
            for a in record.alerts
        ]
        sections.append(DashboardSection(
            title="Alertes",
            widgets=[AlertWidget(id="alerts", items=alert_items)],
        ))

    # Section "Diagnostics et traitements" : un CardWidget par diagnostic et médicament
    diag_med_cards: list = []
    for d in record.diagnostics:
        diag_med_cards.append(CardWidget(
            id=f"diag-{d.id}",
            title=d.label,
            subtitle=d.icd10_code,
            confidence_badge=d.confidence if d.confidence < 1.0 else None,
        ))
    for m in record.medications:
        diag_med_cards.append(CardWidget(
            id=f"med-{m.id}",
            title=m.name,
            subtitle=f"{m.dosage} — {m.frequency}",
            confidence_badge=m.confidence if m.confidence < 1.0 else None,
        ))
    if diag_med_cards:
        sections.append(DashboardSection(
            title="Diagnostics et traitements",
            widgets=diag_med_cards,
        ))

    # Section "Parcours" : frise chronologique (étapes de traitement + rendez-vous)
    events = [
        TimelineEvent(
            label=step.label,
            date=step.scheduled_date.isoformat() if step.scheduled_date else None,
            status=step.status.value,
        )
        for step in record.treatment_steps
    ] + [
        TimelineEvent(
            label=appt.label,
            date=appt.date.isoformat(),
            status=None,
        )
        for appt in record.appointments
    ]
    if events:
        sections.append(DashboardSection(
            title="Votre parcours",
            widgets=[TimelineWidget(id="timeline", events=events)],
        ))

    # Section "Objectifs" : une barre de progression par ClinicalGoal complet
    goal_widgets = []
    for g in record.clinical_goals:
        if g.target_value is None or g.current_value is None or g.unit is None:
            continue
        progress = _compute_progress_percent(g.current_value, g.target_value)
        goal_widgets.append(GoalProgressWidget(
            id=f"goal-{g.id}",
            label=g.label,
            current_value=g.current_value,
            target_value=g.target_value,
            unit=g.unit,
            progress_percent=progress,
        ))
    if goal_widgets:
        sections.append(DashboardSection(title="Objectifs", widgets=goal_widgets))

    return DashboardSchema(patient_header=header, sections=sections)


def _compute_progress_percent(current: float, target: float) -> float:
    """Calcule un pourcentage de progression simple.
    Hypothèse simplifiée (documentée) : on suppose que se rapprocher de la cible
    est l'objectif, peu importe le sens (croissant ou décroissant)."""
    if target == 0:
        return 100.0 if current == 0 else 0.0
    ratio = 1 - abs(current - target) / max(abs(target), 1e-6)
    return round(max(0.0, min(100.0, ratio * 100)), 1)