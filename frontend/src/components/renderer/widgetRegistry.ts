import type { ComponentType } from "react";
import type { Widget } from "../../types/dashboardSchema";
import CardWidget from "./widgets/CardWidget";
import AlertWidget from "./widgets/AlertWidget";
import TimelineWidget from "./widgets/TimelineWidget";
import GoalProgressWidget from "./widgets/GoalProgressWidget";

// Registre : associe chaque valeur du discriminant "type" à son composant React.
// C'est le point d'extension unique du moteur : ajouter un widget = ajouter une ligne ici,
// sans toucher au DashboardRenderer.
export const widgetRegistry: Record<Widget["type"], ComponentType<any>> = {
  card: CardWidget,
  alert: AlertWidget,
  timeline: TimelineWidget,
  goal_progress: GoalProgressWidget,
};
