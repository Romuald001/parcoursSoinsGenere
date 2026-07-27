import axios from "axios";
import type { DashboardSchema } from "../types/dashboardSchema";
import { AUTH_STORAGE_KEY } from "../auth/storageKey";

const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (raw) {
      const { token } = JSON.parse(raw);
      if (token) config.headers.Authorization = `Bearer ${token}`;
    }
  } catch {
    // stockage corrompu : la requête part sans token
  }
  return config;
});

export type PatientRecord = Record<string, unknown>;
export type PersonalizedSummary = Record<string, unknown>;

interface PipelineOutcome {
  schema: DashboardSchema;
  patientId: string | null;
  doctorName: string | null;
}

export async function extractPatientRecord(rawNote: string): Promise<PatientRecord> {
  const { data } = await apiClient.post<PatientRecord>("/extract", { raw_note: rawNote });
  return data;
}

export async function validatePatientRecord(record: PatientRecord): Promise<PatientRecord> {
  const { data } = await apiClient.post<PatientRecord>("/validate", record);
  return data;
}

export async function personalizeSummary(record: PatientRecord): Promise<PersonalizedSummary> {
  const { data } = await apiClient.post<PersonalizedSummary>("/personalize", record);
  return data;
}

export async function generateUI(
  record: PatientRecord,
  summary: PersonalizedSummary
): Promise<PipelineOutcome> {
  const response = await apiClient.post<DashboardSchema>("/generate-ui", {
    patient_record: record,
    personalized_summary: summary,
  });
  return {
    schema: response.data,
    patientId: (response.headers["x-patient-id"] as string) ?? null,
    doctorName: (response.headers["x-doctor-name"] as string) ?? null,
  };
}

export async function runFullPipeline(rawNote: string): Promise<PipelineOutcome> {
  const response = await apiClient.post<DashboardSchema>("/pipeline/run", { raw_note: rawNote });
  return {
    schema: response.data,
    patientId: (response.headers["x-patient-id"] as string) ?? null,
    doctorName: (response.headers["x-doctor-name"] as string) ?? null,
  };
}

export async function getMyDashboard(): Promise<{ schema: DashboardSchema; doctorName: string | null }> {
  const response = await apiClient.get<DashboardSchema>("/me/dashboard");
  return { schema: response.data, doctorName: (response.headers["x-doctor-name"] as string) ?? null };
}

export async function registerDoctor(email: string, password: string, fullName?: string): Promise<void> {
  await apiClient.post("/auth/register-doctor", { email, password, full_name: fullName || undefined });
}

export async function listDoctors(): Promise<{ id: string; email: string; created_at: string }[]> {
  const { data } = await apiClient.get("/admin/doctors");
  return data;
}

export async function registerPatientAccount(params: {
  patientId: string;
  email?: string;
  phone?: string;
  password: string;
}): Promise<void> {
  await apiClient.post("/auth/register-patient-account", {
    patient_id: params.patientId,
    email: params.email || undefined,
    phone: params.phone || undefined,
    password: params.password,
  });
}

export interface ConsultationSummary {
  id: string;
  created_at: string;
  raw_note: string;
  doctor_name: string | null;
  diagnostics: string[];
  clinical_goals: { label: string; unit: string }[];
}

export async function getPatientConsultations(patientId: string): Promise<ConsultationSummary[]> {
  const { data } = await apiClient.get(`/patients/${patientId}/consultations`);
  return data;
}

export interface GoalTrendPoint {
  date: string;
  current_value: number;
  target_value: number;
  unit: string;
}

export async function getGoalTrend(patientId: string, goalLabel: string): Promise<GoalTrendPoint[]> {
  const { data } = await apiClient.get(`/patients/${patientId}/goal-trend/${encodeURIComponent(goalLabel)}`);
  return data;
}

export async function getPatientLatestDashboard(patientId: string): Promise<DashboardSchema> {
  const { data } = await apiClient.get(`/patients/${patientId}/dashboard/latest`);
  return data;
}

export interface PatientSummary {
  id: string;
  full_name: string;
  birth_date: string;
  consultation_count: number;
}

export async function listPatients(): Promise<PatientSummary[]> {
  const { data } = await apiClient.get<PatientSummary[]>("/patients");
  return data;
}

export interface ConsultationDetail extends ConsultationSummary {
  doctor_name: string | null;
}

export async function getConsultationDashboard(
  patientId: string,
  consultationId: string
): Promise<{ schema: DashboardSchema; doctorName: string | null }> {
  const response = await apiClient.get<DashboardSchema>(
    `/patients/${patientId}/consultations/${consultationId}/dashboard`
  );
  return { schema: response.data, doctorName: (response.headers["x-doctor-name"] as string) ?? null };
}

export async function continueConsultation(
  patientId: string,
  rawNote: string
): Promise<{ schema: DashboardSchema; doctorName: string | null }> {
  const response = await apiClient.post<DashboardSchema>(`/patients/${patientId}/continue`, { raw_note: rawNote });
  return { schema: response.data, doctorName: (response.headers["x-doctor-name"] as string) ?? null };
}


export default apiClient;
