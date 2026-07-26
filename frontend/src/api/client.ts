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
  return { schema: response.data, patientId: (response.headers["x-patient-id"] as string) ?? null };
}

export async function runFullPipeline(rawNote: string): Promise<PipelineOutcome> {
  const response = await apiClient.post<DashboardSchema>("/pipeline/run", { raw_note: rawNote });
  return { schema: response.data, patientId: (response.headers["x-patient-id"] as string) ?? null };
}

export async function getMyDashboard(): Promise<DashboardSchema> {
  const { data } = await apiClient.get<DashboardSchema>("/me/dashboard");
  return data;
}

export async function registerDoctor(email: string, password: string): Promise<void> {
  await apiClient.post("/auth/register-doctor", { email, password });
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

export default apiClient;
