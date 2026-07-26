// Miroir TypeScript exact du schéma Pydantic (app/domain/ui_schema/dashboard_schema.py)
// Le champ "type" sert de discriminant, exactement comme côté backend (Union discriminée).

export interface PatientHeaderData {
  full_name: string;
  age: number;
  greeting: string;
}

export interface CardWidgetData {
  type: "card";
  id: string;
  title: string;
  subtitle?: string | null;
  description?: string | null;
  confidence_badge?: number | null;
}

export interface AlertWidgetItem {
  severity: "info" | "warning" | "critical";
  message: string;
}

export interface AlertWidgetData {
  type: "alert";
  id: string;
  items: AlertWidgetItem[];
}

export interface TimelineEvent {
  label: string;
  date?: string | null;
  status?: string | null;
}

export interface TimelineWidgetData {
  type: "timeline";
  id: string;
  events: TimelineEvent[];
}

export interface GoalProgressWidgetData {
  type: "goal_progress";
  id: string;
  label: string;
  current_value: number;
  target_value: number;
  unit: string;
  progress_percent: number;
}

// Union discriminée : TypeScript peut restreindre le type exact
// selon la valeur du champ "type", comme un pattern matching.
export type Widget =
  | CardWidgetData
  | AlertWidgetData
  | TimelineWidgetData
  | GoalProgressWidgetData;

export interface DashboardSection {
  title: string;
  widgets: Widget[];
}

export interface DashboardSchema {
  patient_header: PatientHeaderData;
  sections: DashboardSection[];
}